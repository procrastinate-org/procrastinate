from __future__ import annotations

import datetime
import json
import logging
from collections.abc import Awaitable, Iterable
from typing import Any, NoReturn, Protocol

from procrastinate import connector, exceptions, jobs, sql, utils

logger = logging.getLogger(__name__)

QUEUEING_LOCK_CONSTRAINT = "procrastinate_jobs_queueing_lock_idx_v1"

# TODO: Only necessary to make it work with the pre-migration of v3.0.0.
# We can remove this in the next minor version.
QUEUEING_LOCK_CONSTRAINT_LEGACY = "procrastinate_jobs_queueing_lock_idx"


class NotificationCallback(Protocol):
    def __call__(
        self, *, channel: str, notification: jobs.Notification
    ) -> Awaitable[None]: ...


def get_channel_for_queues(queues: Iterable[str] | None = None) -> Iterable[str]:
    if queues is None:
        return ["procrastinate_any_queue_v1"]
    else:
        return ["procrastinate_queue_v1#" + queue for queue in queues]


class JobManager:
    def __init__(self, connector: connector.BaseConnector):
        self.connector = connector

    async def defer_job_async(self, job: jobs.Job) -> jobs.Job:
        """
        Add a job in its queue for later processing by a worker.

        Parameters
        ----------
        job:
            The job to defer

        Returns
        -------
        :
            A copy of the job instance with the id set.
        """
        # Make sure this code stays synchronized with .defer_job()
        try:
            result = await self.connector.execute_query_one_async(
                **self._defer_job_query_kwargs(job=job)
            )
        except exceptions.UniqueViolation as exc:
            self._raise_already_enqueued(exc=exc, queueing_lock=job.queueing_lock)

        return job.evolve(id=result["id"], status=jobs.Status.TODO.value)

    def defer_job(self, job: jobs.Job) -> jobs.Job:
        """
        Sync version of `defer_job_async`.
        """
        try:
            result = self.connector.get_sync_connector().execute_query_one(
                **self._defer_job_query_kwargs(job=job)
            )
        except exceptions.UniqueViolation as exc:
            self._raise_already_enqueued(exc=exc, queueing_lock=job.queueing_lock)

        return job.evolve(id=result["id"], status=jobs.Status.TODO.value)

    def _defer_job_query_kwargs(self, job: jobs.Job) -> dict[str, Any]:
        return {
            "query": sql.queries["defer_job"],
            "task_name": job.task_name,
            "queue": job.queue,
            "priority": job.priority,
            "lock": job.lock,
            "queueing_lock": job.queueing_lock,
            "args": job.task_kwargs,
            "scheduled_at": job.scheduled_at,
        }

    def _raise_already_enqueued(
        self, exc: exceptions.UniqueViolation, queueing_lock: str | None
    ) -> NoReturn:
        if exc.constraint_name in [
            QUEUEING_LOCK_CONSTRAINT,
            QUEUEING_LOCK_CONSTRAINT_LEGACY,
        ]:
            raise exceptions.AlreadyEnqueued(
                "Job cannot be enqueued: there is already a job in the queue "
                f"with the queueing lock {queueing_lock}"
            ) from exc
        raise exc

    async def defer_periodic_job(
        self,
        job: jobs.Job,
        periodic_id: str,
        defer_timestamp: int,
    ) -> int | None:
        """
        Defer a periodic job, ensuring that no other worker will defer a job for the
        same timestamp.

        If the job was deferred, return its id.
        If the job was not deferred, return None.
        """
        # If we mutate the existing task_kwargs dict, we could have unintended side
        # effects
        if job.task_kwargs.get("timestamp") != defer_timestamp:
            raise exceptions.InvalidTimestamp

        # schedule_at and schedule_in are meaningless in this context, we ignore them
        try:
            result = await self.connector.execute_query_one_async(
                query=sql.queries["defer_periodic_job"],
                task_name=job.task_name,
                defer_timestamp=defer_timestamp,
                periodic_id=periodic_id,
                queue=job.queue,
                priority=job.priority,
                lock=job.lock,
                queueing_lock=job.queueing_lock,
                args=job.task_kwargs,
            )
        except exceptions.UniqueViolation as exc:
            self._raise_already_enqueued(exc=exc, queueing_lock=job.queueing_lock)

        return result["id"]

    async def fetch_job(self, queues: Iterable[str] | None) -> jobs.Job | None:
        """
        Select a job in the queue, and mark it as doing.
        The worker selecting a job is then responsible for running it, and then
        to update the DB with the new status once it's done.

        Parameters
        ----------
        queues:
            Filter by job queue names

        Returns
        -------
        :
            None if no suitable job was found. The job otherwise.
        """

        row = await self.connector.execute_query_one_async(
            query=sql.queries["fetch_job"], queues=queues
        )

        # fetch_tasks will always return a row, but is there's no relevant
        # value, it will all be None
        if row["id"] is None:
            return None

        return jobs.Job.from_row(row)

    async def update_heartbeats(self, jobs: list[jobs.Job]) -> None:
        """
        Update the heartbeats of the given jobs.
        """
        await self.connector.execute_query_async(
            query=sql.queries["update_heartbeats"],
            job_ids=[job.id for job in jobs],
        )

    async def get_stalled_jobs_by_heartbeat(
        self,
        max_seconds_since_heartbeat: int,
        queue: str | None = None,
        task_name: str | None = None,
    ) -> Iterable[jobs.Job]:
        """
        Return all jobs that have been in ``doing`` state for more than a given time.

        Parameters
        ----------
        max_seconds_since_heartbeat:
            Only jobs which heartbeat is older than this will be returned.
        queue:
            Filter by job queue name
        task_name:
            Filter by job task name
        """
        rows = await self.connector.execute_query_all_async(
            query=sql.queries["select_stalled_jobs_by_heartbeat"],
            max_seconds_since_heartbeat=max_seconds_since_heartbeat,
            queue=queue,
            task_name=task_name,
        )
        return [jobs.Job.from_row(row) for row in rows]

    async def get_stalled_jobs_by_started(
        self,
        max_seconds_since_started: int,
        queue: str | None = None,
        task_name: str | None = None,
    ) -> Iterable[jobs.Job]:
        """
        Return all jobs that have been in ``doing`` state for more than a given time.

        Parameters
        ----------
        max_seconds_since_started:
            Only jobs that have been in ``doing`` state for longer than this will be
            returned.
        queue:
            Filter by job queue name
        task_name:
            Filter by job task name
        """
        rows = await self.connector.execute_query_all_async(
            query=sql.queries["select_stalled_jobs_by_started"],
            max_seconds_since_started=max_seconds_since_started,
            queue=queue,
            task_name=task_name,
        )
        return [jobs.Job.from_row(row) for row in rows]

    async def get_stalled_jobs(
        self,
        nb_seconds: int,
        queue: str | None = None,
        task_name: str | None = None,
    ) -> Iterable[jobs.Job]:
        """
        This method is deprecated, use ``get_stalled_jobs_by_started`` or
        ``get_stalled_jobs_by_heartbeat`` instead.
        """
        return await self.get_stalled_jobs_by_started(
            max_seconds_since_started=nb_seconds,
            queue=queue,
            task_name=task_name,
        )

    async def delete_old_jobs(
        self,
        nb_hours: int,
        queue: str | None = None,
        include_failed: bool | None = False,
        include_cancelled: bool | None = False,
        include_aborted: bool | None = False,
    ) -> None:
        """
        Delete jobs that have reached a final state (``succeeded``, ``failed``,
        ``cancelled``, or ``aborted``). By default, only considers jobs that have
        succeeded.

        Parameters
        ----------
        nb_hours:
            Consider jobs that been in a final state for more than ``nb_hours``
        queue:
            Filter by job queue name
        include_failed:
            If ``True``, also consider errored jobs. ``False`` by default
        include_cancelled:
            If ``True``, also consider cancelled jobs. ``False`` by default.
        include_aborted:
            If ``True``, also consider aborted jobs. ``False`` by default.
        """
        # We only consider finished jobs by default
        statuses = [jobs.Status.SUCCEEDED.value]
        if include_failed:
            statuses.append(jobs.Status.FAILED.value)
        if include_cancelled:
            statuses.append(jobs.Status.CANCELLED.value)
        if include_aborted:
            statuses.append(jobs.Status.ABORTED.value)

        await self.connector.execute_query_async(
            query=sql.queries["delete_old_jobs"],
            nb_hours=nb_hours,
            queue=queue,
            statuses=statuses,
        )

    async def finish_job(
        self,
        job: jobs.Job,
        status: jobs.Status,
        delete_job: bool,
    ) -> None:
        """
        Set a job to its final state (``succeeded``, ``failed`` or ``aborted``).

        Parameters
        ----------
        job:
        status:
            ``succeeded``, ``failed`` or ``aborted``
        """
        assert job.id  # TODO remove this
        await self.finish_job_by_id_async(
            job_id=job.id, status=status, delete_job=delete_job
        )

    async def finish_job_by_id_async(
        self,
        job_id: int,
        status: jobs.Status,
        delete_job: bool,
    ) -> None:
        await self.connector.execute_query_async(
            query=sql.queries["finish_job"],
            job_id=job_id,
            status=status.value,
            delete_job=delete_job,
        )

    def cancel_job_by_id(
        self, job_id: int, abort: bool = False, delete_job: bool = False
    ) -> bool:
        """
        Cancel a job by id.

        Parameters
        ----------
        job_id:
            The id of the job to cancel
        abort:
            If True, a job will be marked for abortion, but the task itself has to
            respect the abortion request. If False, only jobs in ``todo`` state will
            be set to ``cancelled`` and won't be processed by a worker anymore.
        delete_job:
            If True, the job will be deleted from the database after being cancelled. Does
            not affect the jobs that should be aborted.

        Returns
        -------
        :
            If True, the job was cancelled (or its abortion was requested). If False,
            nothing was done: either there is no job with this id or it's not in a state
            where it may be cancelled (i.e. `todo` or `doing`)
        """
        result = self.connector.get_sync_connector().execute_query_one(
            query=sql.queries["cancel_job"],
            job_id=job_id,
            abort=abort,
            delete_job=delete_job,
        )

        if result["id"] is None:
            return False

        assert result["id"] == job_id
        return True

    async def cancel_job_by_id_async(
        self, job_id: int, abort: bool = False, delete_job=False
    ) -> bool:
        """
        Cancel a job by id.

        Parameters
        ----------
        job_id:
            The id of the job to cancel
        abort:
            If True, a job will be marked for abortion, but the task itself has to
            respect the abortion request. If False, only jobs in ``todo`` state will
            be set to ``cancelled`` and won't be processed by a worker anymore.
        delete_job:
            If True, the job will be deleted from the database after being cancelled. Does
            not affect the jobs that should be aborted.

        Returns
        -------
        :
            If True, the job was cancelled (or its abortion was requested). If False,
            nothing was done: either there is no job with this id or it's not in a state
            where it may be cancelled (i.e. `todo` or `doing`)
        """
        result = await self.connector.execute_query_one_async(
            query=sql.queries["cancel_job"],
            job_id=job_id,
            abort=abort,
            delete_job=delete_job,
        )

        if result["id"] is None:
            return False

        assert result["id"] == job_id
        return True

    def get_job_status(self, job_id: int) -> jobs.Status:
        """
        Get the status of a job by id.

        Parameters
        ----------
        job_id:
            The id of the job to get the status of

        Returns
        -------
        :
        """
        result = self.connector.get_sync_connector().execute_query_one(
            query=sql.queries["get_job_status"], job_id=job_id
        )
        return jobs.Status(result["status"])

    async def get_job_status_async(self, job_id: int) -> jobs.Status:
        """
        Get the status of a job by id.

        Parameters
        ----------
        job_id:
            The id of the job to get the status of

        Returns
        -------
        :
        """
        result = await self.connector.execute_query_one_async(
            query=sql.queries["get_job_status"], job_id=job_id
        )
        return jobs.Status(result["status"])

    async def retry_job(
        self,
        job: jobs.Job,
        retry_at: datetime.datetime | None = None,
        priority: int | None = None,
        queue: str | None = None,
        lock: str | None = None,
    ) -> None:
        """
        Indicates that a job should be retried later.

        Parameters
        ----------
        job:
        retry_at:
            If set at present time or in the past, the job may be retried immediately.
            Otherwise, the job will be retried no sooner than this date & time.
            Should be timezone-aware (even if UTC). Defaults to present time.
        priority:
            If set, the job will be retried with this priority. If not set, the priority
            remains unchanged.
        queue:
            If set, the job will be retried on this queue. If not set, the queue remains
            unchanged.
        lock:
            If set, the job will be retried with this lock. If not set, the lock remains
            unchanged.
        """
        assert job.id  # TODO remove this
        await self.retry_job_by_id_async(
            job_id=job.id,
            retry_at=retry_at or utils.utcnow(),
            priority=priority,
            queue=queue,
            lock=lock,
        )

    async def retry_job_by_id_async(
        self,
        job_id: int,
        retry_at: datetime.datetime,
        priority: int | None = None,
        queue: str | None = None,
        lock: str | None = None,
    ) -> None:
        """
        Indicates that a job should be retried later.

        Parameters
        ----------
        job_id:
        retry_at:
            If set at present time or in the past, the job may be retried immediately.
            Otherwise, the job will be retried no sooner than this date & time.
            Should be timezone-aware (even if UTC).
        priority:
            If set, the job will be retried with this priority. If not set, the priority
            remains unchanged.
        queue:
            If set, the job will be retried on this queue. If not set, the queue remains
            unchanged.
        lock:
            If set, the job will be retried with this lock. If not set, the lock remains
            unchanged.
        """
        await self.connector.execute_query_async(
            query=sql.queries["retry_job"],
            job_id=job_id,
            retry_at=retry_at,
            new_priority=priority,
            new_queue_name=queue,
            new_lock=lock,
        )

    def retry_job_by_id(
        self,
        job_id: int,
        retry_at: datetime.datetime,
        priority: int | None = None,
        queue: str | None = None,
        lock: str | None = None,
    ) -> None:
        """
        Sync version of `retry_job_by_id_async`.
        """
        self.connector.get_sync_connector().execute_query(
            query=sql.queries["retry_job"],
            job_id=job_id,
            retry_at=retry_at,
            new_priority=priority,
            new_queue_name=queue,
            new_lock=lock,
        )

    async def listen_for_jobs(
        self,
        *,
        on_notification: NotificationCallback,
        queues: Iterable[str] | None = None,
    ) -> None:
        """
        Listens to job notifications from the database, and invokes the callback each time an
        notification is received.

        This coroutine either returns ``None`` upon calling if it cannot start
        listening or does not return and needs to be cancelled to end.

        Parameters
        ----------
        on_notification : ``connector.Notify``
            A coroutine that will be called and awaited every time a notification is received
        queues : ``Optional[Iterable[str]]``
            If ``None``, all notification will be considered. If an iterable of
            queue names is passed, only defer operations on those queues will be
            considered. Defaults to ``None``
        """

        async def handle_notification(channel: str, payload: str):
            notification: jobs.Notification = json.loads(payload)
            logger.debug(
                f"Received {notification['type']} notification from channel",
                extra={channel: channel, payload: payload},
            )
            await on_notification(channel=channel, notification=notification)

        await self.connector.listen_notify(
            on_notification=handle_notification,
            channels=get_channel_for_queues(queues=queues),
        )

    async def check_connection_async(self) -> bool:
        """
        Dummy query, check that the main Procrastinate SQL table exists.
        Raises if there's a connection problem.

        Returns
        -------
        :
            ``True`` if the table exists, ``False`` otherwise.
        """
        result = await self.connector.execute_query_one_async(
            query=sql.queries["check_connection"],
        )
        return result["check"] is not None

    def check_connection(self) -> bool:
        """
        Sync version of `check_connection_async`.
        """
        result = self.connector.get_sync_connector().execute_query_one(
            query=sql.queries["check_connection"],
        )
        return result["check"] is not None

    async def list_jobs_async(
        self,
        id: int | None = None,
        queue: str | None = None,
        task: str | None = None,
        status: str | None = None,
        lock: str | None = None,
        queueing_lock: str | None = None,
    ) -> Iterable[jobs.Job]:
        """
        List all procrastinate jobs given query filters.

        Parameters
        ----------
        id:
            Filter by job ID
        queue:
            Filter by job queue name
        task:
            Filter by job task name
        status:
            Filter by job status (``todo``/``doing``/``succeeded``/``failed``)
        lock:
            Filter by job lock
        queueing_lock:
            Filter by job queueing_lock

        Returns
        -------
        :
        """
        rows = await self.connector.execute_query_all_async(
            query=sql.queries["list_jobs"],
            id=id,
            queue_name=queue,
            task_name=task,
            status=status,
            lock=lock,
            queueing_lock=queueing_lock,
        )
        return [jobs.Job.from_row(row) for row in rows]

    def list_jobs(
        self,
        id: int | None = None,
        queue: str | None = None,
        task: str | None = None,
        status: str | None = None,
        lock: str | None = None,
        queueing_lock: str | None = None,
    ) -> list[jobs.Job]:
        """
        Sync version of `list_jobs_async`
        """
        rows = self.connector.get_sync_connector().execute_query_all(
            query=sql.queries["list_jobs"],
            id=id,
            queue_name=queue,
            task_name=task,
            status=status,
            lock=lock,
            queueing_lock=queueing_lock,
        )
        return [jobs.Job.from_row(row) for row in rows]

    async def list_queues_async(
        self,
        queue: str | None = None,
        task: str | None = None,
        status: str | None = None,
        lock: str | None = None,
    ) -> Iterable[dict[str, Any]]:
        """
        List all queues and number of jobs per status for each queue.

        Parameters
        ----------
        queue:
            Filter by job queue name
        task:
            Filter by job task name
        status:
            Filter by job status (``todo``/``doing``/``succeeded``/``failed``)
        lock:
            Filter by job lock

        Returns
        -------
        :
            A list of dictionaries representing queues stats (``name``, ``jobs_count``,
            ``todo``, ``doing``, ``succeeded``, ``failed``, ``cancelled``, ``aborted``).
        """
        return [
            {
                "name": row["name"],
                "jobs_count": row["jobs_count"],
                "todo": row["stats"].get("todo", 0),
                "doing": row["stats"].get("doing", 0),
                "succeeded": row["stats"].get("succeeded", 0),
                "failed": row["stats"].get("failed", 0),
                "cancelled": row["stats"].get("cancelled", 0),
                "aborted": row["stats"].get("aborted", 0),
            }
            for row in await self.connector.execute_query_all_async(
                query=sql.queries["list_queues"],
                queue_name=queue,
                task_name=task,
                status=status,
                lock=lock,
            )
        ]

    def list_queues(
        self,
        queue: str | None = None,
        task: str | None = None,
        status: str | None = None,
        lock: str | None = None,
    ) -> Iterable[dict[str, Any]]:
        """
        Sync version of `list_queues_async`
        """
        return [
            {
                "name": row["name"],
                "jobs_count": row["jobs_count"],
                "todo": row["stats"].get("todo", 0),
                "doing": row["stats"].get("doing", 0),
                "succeeded": row["stats"].get("succeeded", 0),
                "failed": row["stats"].get("failed", 0),
                "cancelled": row["stats"].get("cancelled", 0),
                "aborted": row["stats"].get("aborted", 0),
            }
            for row in self.connector.get_sync_connector().execute_query_all(
                query=sql.queries["list_queues"],
                queue_name=queue,
                task_name=task,
                status=status,
                lock=lock,
            )
        ]

    async def list_tasks_async(
        self,
        queue: str | None = None,
        task: str | None = None,
        status: str | None = None,
        lock: str | None = None,
    ) -> Iterable[dict[str, Any]]:
        """
        List all tasks and number of jobs per status for each task.

        Parameters
        ----------
        queue:
            Filter by job queue name
        task:
            Filter by job task name
        status:
            Filter by job status (``todo``/``doing``/``succeeded``/``failed``)
        lock:
            Filter by job lock

        Returns
        -------
        :
            A list of dictionaries representing tasks stats (``name``, ``jobs_count``,
            ``todo``, ``doing``, ``succeeded``, ``failed``, ``cancelled``, ``aborted``).
        """
        return [
            {
                "name": row["name"],
                "jobs_count": row["jobs_count"],
                "todo": row["stats"].get("todo", 0),
                "doing": row["stats"].get("doing", 0),
                "succeeded": row["stats"].get("succeeded", 0),
                "failed": row["stats"].get("failed", 0),
                "cancelled": row["stats"].get("cancelled", 0),
                "aborted": row["stats"].get("aborted", 0),
            }
            for row in await self.connector.execute_query_all_async(
                query=sql.queries["list_tasks"],
                queue_name=queue,
                task_name=task,
                status=status,
                lock=lock,
            )
        ]

    def list_tasks(
        self,
        queue: str | None = None,
        task: str | None = None,
        status: str | None = None,
        lock: str | None = None,
    ) -> Iterable[dict[str, Any]]:
        """
        Sync version of `list_queues`
        """
        return [
            {
                "name": row["name"],
                "jobs_count": row["jobs_count"],
                "todo": row["stats"].get("todo", 0),
                "doing": row["stats"].get("doing", 0),
                "succeeded": row["stats"].get("succeeded", 0),
                "failed": row["stats"].get("failed", 0),
                "cancelled": row["stats"].get("cancelled", 0),
                "aborted": row["stats"].get("aborted", 0),
            }
            for row in self.connector.get_sync_connector().execute_query_all(
                query=sql.queries["list_tasks"],
                queue_name=queue,
                task_name=task,
                status=status,
                lock=lock,
            )
        ]

    async def list_locks_async(
        self,
        queue: str | None = None,
        task: str | None = None,
        status: str | None = None,
        lock: str | None = None,
    ) -> Iterable[dict[str, Any]]:
        """
        List all locks and number of jobs per lock for each lock value.

        Parameters
        ----------
        queue:
            Filter by job queue name
        task:
            Filter by job task name
        status:
            Filter by job status (``todo``/``doing``/``succeeded``/``failed``)
        lock:
            Filter by job lock

        Returns
        -------
        :
            A list of dictionaries representing locks stats (``name``, ``jobs_count``,
            ``todo``, ``doing``, ``succeeded``, ``failed``, ``cancelled``, ``aborted``).
        """
        result = []
        for row in await self.connector.execute_query_all_async(
            query=sql.queries["list_locks"],
            queue_name=queue,
            task_name=task,
            status=status,
            lock=lock,
        ):
            result.append(
                {
                    "name": row["name"],
                    "jobs_count": row["jobs_count"],
                    "todo": row["stats"].get("todo", 0),
                    "doing": row["stats"].get("doing", 0),
                    "succeeded": row["stats"].get("succeeded", 0),
                    "failed": row["stats"].get("failed", 0),
                    "cancelled": row["stats"].get("cancelled", 0),
                    "aborted": row["stats"].get("aborted", 0),
                }
            )
        return result

    def list_locks(
        self,
        queue: str | None = None,
        task: str | None = None,
        status: str | None = None,
        lock: str | None = None,
    ) -> Iterable[dict[str, Any]]:
        """
        Sync version of `list_queues`
        """
        result = []
        for row in self.connector.get_sync_connector().execute_query_all(
            query=sql.queries["list_locks"],
            queue_name=queue,
            task_name=task,
            status=status,
            lock=lock,
        ):
            result.append(
                {
                    "name": row["name"],
                    "jobs_count": row["jobs_count"],
                    "todo": row["stats"].get("todo", 0),
                    "doing": row["stats"].get("doing", 0),
                    "succeeded": row["stats"].get("succeeded", 0),
                    "failed": row["stats"].get("failed", 0),
                    "cancelled": row["stats"].get("cancelled", 0),
                    "aborted": row["stats"].get("aborted", 0),
                }
            )
        return result

    async def list_jobs_to_abort_async(self, queue: str | None = None) -> Iterable[int]:
        """
        List ids of running jobs to abort
        """
        rows = await self.connector.execute_query_all_async(
            query=sql.queries["list_jobs_to_abort"], queue_name=queue
        )
        return [row["id"] for row in rows]
