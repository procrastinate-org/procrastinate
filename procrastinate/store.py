import asyncio
import datetime
import uuid
from typing import Any, Dict, Iterable, Optional

from procrastinate import connector, exceptions, jobs, sql


def get_channel_for_queues(queues: Optional[Iterable[str]] = None) -> Iterable[str]:
    if queues is None:
        return ["procrastinate_any_queue"]
    else:
        return ["procrastinate_queue#" + queue for queue in queues]


class JobStore:
    def __init__(
        self, connector: connector.BaseConnector,
    ):
        self.connector = connector

    async def defer_job_async(self, job: jobs.Job) -> int:
        # Make sure this code stays synchronized with .defer_job()
        try:
            result = await self.connector.execute_query_one_async(
                **self._defer_job_query_kwargs(job=job)
            )
        except exceptions.UniqueViolation as exc:
            self._raise_already_enqueued(exc=exc, job=job)

        return result["id"]

    def defer_job(self, job: jobs.Job) -> int:
        try:
            result = self.connector.execute_query_one(
                **self._defer_job_query_kwargs(job=job)
            )
        except exceptions.UniqueViolation as exc:
            self._raise_already_enqueued(exc=exc, job=job)

        return result["id"]

    def _defer_job_query_kwargs(self, job: jobs.Job) -> Dict[str, Any]:

        return {
            "query": sql.queries["defer_job"],
            "task_name": job.task_name,
            "lock": job.lock or str(uuid.uuid4()),
            "queueing_lock": job.queueing_lock,
            "args": job.task_kwargs,
            "scheduled_at": job.scheduled_at,
            "queue": job.queue,
        }

    def _raise_already_enqueued(self, exc: exceptions.UniqueViolation, job: jobs.Job):
        if exc.constraint_name == connector.QUEUEING_LOCK_CONSTRAINT:
            raise exceptions.AlreadyEnqueued(
                "Job cannot be enqueued: there is already a job in the queue "
                f"with the lock {job.queueing_lock}"
            ) from exc
        raise exc

    async def defer_periodic_job(self, task, defer_timestamp) -> Optional[int]:
        result = await self.connector.execute_query_one_async(
            query=sql.queries["defer_periodic_job"],
            queue=task.queue,
            task_name=task.name,
            defer_timestamp=defer_timestamp,
        )
        return result["id"]

    async def fetch_job(self, queues: Optional[Iterable[str]]) -> Optional[jobs.Job]:

        row = await self.connector.execute_query_one_async(
            query=sql.queries["fetch_job"], queues=queues
        )

        # fetch_tasks will always return a row, but is there's no relevant
        # value, it will all be None
        if row["id"] is None:
            return None

        return jobs.Job.from_row(row)

    async def get_stalled_jobs(
        self,
        nb_seconds: int,
        queue: Optional[str] = None,
        task_name: Optional[str] = None,
    ) -> Iterable[jobs.Job]:

        rows = await self.connector.execute_query_all_async(
            query=sql.queries["select_stalled_jobs"],
            nb_seconds=nb_seconds,
            queue=queue,
            task_name=task_name,
        )
        return [jobs.Job.from_row(row) for row in rows]

    async def delete_old_jobs(
        self,
        nb_hours: int,
        queue: Optional[str] = None,
        include_error: Optional[bool] = False,
    ) -> None:
        # We only consider finished jobs by default
        if not include_error:
            statuses = [jobs.Status.SUCCEEDED.value]
        else:
            statuses = [jobs.Status.SUCCEEDED.value, jobs.Status.FAILED.value]

        await self.connector.execute_query_async(
            query=sql.queries["delete_old_jobs"],
            nb_hours=nb_hours,
            queue=queue,
            statuses=tuple(statuses),
        )

    async def finish_job(
        self,
        job: jobs.Job,
        status: jobs.Status,
        scheduled_at: Optional[datetime.datetime] = None,
    ) -> None:
        assert job.id  # TODO remove this
        await self.connector.execute_query_async(
            query=sql.queries["finish_job"],
            job_id=job.id,
            status=status.value,
            scheduled_at=scheduled_at,
        )

    async def listen_for_jobs(
        self, *, event: asyncio.Event, queues: Optional[Iterable[str]] = None,
    ) -> None:
        await self.connector.listen_notify(
            event=event, channels=get_channel_for_queues(queues=queues)
        )
