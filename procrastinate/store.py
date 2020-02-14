import datetime
from typing import Iterable, Optional

from procrastinate import connector, jobs, sql


def get_channel_for_queues(queues: Optional[Iterable[str]] = None) -> Iterable[str]:
    if queues is None:
        return ["procrastinate_any_queue"]
    else:
        return ["procrastinate_queue#" + queue for queue in queues]


class JobStore:
    def __init__(self, connector: connector.BaseConnector):
        self.connector = connector

    async def wait_for_jobs(self):
        return await self.connector.wait_for_activity()

    # stop, being called in a signal handler, may NOT be an awaitable
    def stop(self):
        self.connector.interrupt_wait()

    async def defer_job(self, job: jobs.Job) -> int:
        result = await self.connector.execute_query_one(
            query=sql.queries["defer_job"],
            task_name=job.task_name,
            lock=job.lock,
            args=job.task_kwargs,
            scheduled_at=job.scheduled_at,
            queue=job.queue,
        )
        return result["id"]

    async def fetch_job(self, queues: Optional[Iterable[str]]) -> Optional[jobs.Job]:

        row = await self.connector.execute_query_one(
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

        rows = await self.connector.execute_query_all(
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

        await self.connector.execute_query(
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
        await self.connector.execute_query(
            query=sql.queries["finish_job"],
            job_id=job.id,
            status=status.value,
            scheduled_at=scheduled_at,
        )

    async def listen_for_jobs(self, queues: Optional[Iterable[str]] = None) -> None:
        for channel_name in get_channel_for_queues(queues=queues):

            await self.connector.execute_query(
                query=self.connector.make_dynamic_query(
                    query=sql.queries["listen_queue"], channel_name=channel_name
                )
            )
