import datetime
import os
import select
from typing import Any, Dict, Iterable, Iterator, List, Optional, AsyncGenerator

from procrastinate import jobs, sql, types

SOCKET_TIMEOUT = 5.0  # seconds

# Because of how async works, it's very hard to make a common class that will
# manage both sync and async, because the caller needs to know if it needs
# to await it or not, and it needs to know whether to await its I/Os or not.
# Consequently, there are 2 classes (BaseJobStore and AsyncBaseJobStore implementing
# the same-ish API, they're expected to have very little logic on themselves, and
# outsource decisions to pure functions (without I/O) for consistency.


class SyncActivityMonitor:
    def __init__(self, selectable: types.Selectable, timeout: float = SOCKET_TIMEOUT):
        """
        Wait for activity on the selectable (fileno) object until something happens,
        or timeout is reached. Wait using :py:func:`Stopper.wait` or cancel the wait
        by calling :py:func:`Stopper.interrupt`

        Parameters
        ----------
        selectable : types.Selectable
            Integer or object with a ``.fileno() -> int`` method to monitor
        timeout : float, optional
            Number of seconds to wait, by default SOCKET_TIMEOUT
        """
        self.selectable = selectable
        self.read_interrupter, self.write_interrupter = os.pipe()
        self.timeout = timeout

    def interrupt(self):
        os.write(self.write_interrupter, b"s")

    def wait(self) -> None:

        ready_fds = select.select(
            [self.selectable, self.read_interrupter], [], [], self.timeout
        )
        # Don't let things accumulate in the pipe
        if self.read_interrupter in ready_fds[0]:
            os.read(self.read_interrupter, 1)


def get_channel_for_queues(queues: Optional[Iterable[str]] = None) -> Iterable[str]:
    if queues is None:
        return ["procrastinate_any_queue"]
    else:
        return ["procrastinate_queue#" + queue for queue in queues]


class BaseJobStore:
    """
    A JobStore is tasked with storing and fetching the tasks in the postgres database.
    The BaseJobStore makes the high-level logic, using primitives that need to be
    implemented by the specific implementation inheriting it.
    """

    def __init__(self, socket_timeout: float = SOCKET_TIMEOUT):
        self.socket_timeout = socket_timeout
        self._monitor: Optional[SyncActivityMonitor] = None

    def get_sync_store(self) -> "BaseJobStore":
        return self

    def get_connection(self) -> Any:
        raise NotImplementedError

    def execute_query(self, query: str, **arguments: Any) -> None:
        raise NotImplementedError

    def execute_query_one(self, query: str, **arguments: Any) -> Dict[str, Any]:
        raise NotImplementedError

    def execute_query_all(self, query: str, **arguments: Any) -> List[Dict[str, Any]]:
        raise NotImplementedError

    def make_dynamic_query(self, query: str, **identifiers: str) -> str:
        raise NotImplementedError

    def get_monitor(self):
        if not self._monitor:
            self._monitor = SyncActivityMonitor(
                timeout=self.socket_timeout, selectable=self.get_connection()
            )

        return self._monitor

    def wait_for_jobs(self):
        self.get_monitor().wait()

    def stop(self):
        self.get_monitor().interrupt()

    def defer_job(self, job: jobs.Job) -> int:
        return self.execute_query_one(
            query=sql.queries["defer_job"],
            task_name=job.task_name,
            lock=job.lock,
            args=job.task_kwargs,
            scheduled_at=job.scheduled_at,
            queue=job.queue,
        )["id"]

    def fetch_job(self, queues: Optional[Iterable[str]]) -> Optional[jobs.Job]:

        row = self.execute_query_one(query=sql.queries["fetch_job"], queues=queues)

        # fetch_tasks will always return a row, but is there's no relevant
        # value, it will all be None
        if row["id"] is None:
            return None

        return jobs.Job.from_row(row)

    def get_stalled_jobs(
        self,
        nb_seconds: int,
        queue: Optional[str] = None,
        task_name: Optional[str] = None,
    ) -> Iterator[jobs.Job]:

        rows = self.execute_query_all(
            query=sql.queries["select_stalled_jobs"],
            nb_seconds=nb_seconds,
            queue=queue,
            task_name=task_name,
        )
        for row in rows:
            yield jobs.Job.from_row(row)

    def delete_old_jobs(
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

        self.execute_query(
            query=sql.queries["delete_old_jobs"],
            nb_hours=nb_hours,
            queue=queue,
            statuses=tuple(statuses),
        )

    def finish_job(
        self,
        job: jobs.Job,
        status: jobs.Status,
        scheduled_at: Optional[datetime.datetime] = None,
    ) -> None:
        assert job.id
        self.execute_query(
            query=sql.queries["finish_job"],
            job_id=job.id,
            status=status.value,
            scheduled_at=scheduled_at,
        )

    def listen_for_jobs(self, queues: Optional[Iterable[str]] = None) -> None:

        for channel_name in get_channel_for_queues(queues=queues):

            self.execute_query(
                query=self.make_dynamic_query(
                    query=sql.queries["listen_queue"], channel_name=channel_name
                )
            )


class AsyncBaseJobStore:
    def get_sync_store(self) -> BaseJobStore:
        raise NotImplementedError

    async def wait_for_jobs(self):
        raise NotImplementedError

    # stop, being called in a signal handler, may NOT be an awaitable
    def stop(self):
        raise NotImplementedError

    async def execute_query(self, query: str, **arguments: Any) -> None:
        raise NotImplementedError

    async def execute_query_one(self, query: str, **arguments: Any) -> Dict[str, Any]:
        raise NotImplementedError

    async def execute_query_all(
        self, query: str, **arguments: Any
    ) -> List[Dict[str, Any]]:
        raise NotImplementedError

    def make_dynamic_query(self, query: str, **identifiers: str) -> str:
        raise NotImplementedError

    async def defer_job(self, job: jobs.Job) -> int:
        result = await self.execute_query_one(
            query=sql.queries["defer_job"],
            task_name=job.task_name,
            lock=job.lock,
            args=job.task_kwargs,
            scheduled_at=job.scheduled_at,
            queue=job.queue,
        )
        return result["id"]

    async def fetch_job(self, queues: Optional[Iterable[str]]) -> Optional[jobs.Job]:

        row = await self.execute_query_one(
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
    ) -> AsyncGenerator[jobs.Job, None]:

        rows = await self.execute_query_all(
            query=sql.queries["select_stalled_jobs"],
            nb_seconds=nb_seconds,
            queue=queue,
            task_name=task_name,
        )
        for row in rows:
            yield jobs.Job.from_row(row)

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

        await self.execute_query(
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
        await self.execute_query(
            query=sql.queries["finish_job"],
            job_id=job.id,
            status=status.value,
            scheduled_at=scheduled_at,
        )

    async def listen_for_jobs(self, queues: Optional[Iterable[str]] = None) -> None:
        for channel_name in get_channel_for_queues(queues=queues):

            await self.execute_query(
                query=self.make_dynamic_query(
                    query=sql.queries["listen_queue"], channel_name=channel_name
                )
            )
AnyBaseJobStore = Union[BaseJobStore, AsyncBaseJobStore]
