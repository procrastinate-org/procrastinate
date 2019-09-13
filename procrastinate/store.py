import datetime
from typing import Any, Dict, Iterable, Iterator, List, Optional

from procrastinate import jobs, sql


class BaseJobStore:
    def wait_for_jobs(self):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError

    def execute_query(self, query: str, **arguments: Any) -> None:
        raise NotImplementedError

    def execute_query_one(self, query: str, **arguments: Any) -> Dict[str, Any]:
        raise NotImplementedError

    def execute_query_all(self, query: str, **arguments: Any) -> List[Dict[str, Any]]:
        raise NotImplementedError

    def make_dynamic_query(self, query: str, **identifiers: str) -> str:
        raise NotImplementedError

    def defer_job(self, job: jobs.Job) -> int:
        return self.execute_query_one(
            query=sql.queries["insert_job"],
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
            status=status,
            scheduled_at=scheduled_at,
        )

    def listen_for_jobs(self, queues: Optional[Iterable[str]] = None) -> None:
        if queues is None:
            channel_names = ["procrastinate_any_queue"]
        else:
            channel_names = ["procrastinate_queue#" + queue for queue in queues]

        for channel_name in channel_names:

            self.execute_query(
                self.make_dynamic_query(
                    query=sql.queries["listen_queue"], channel_name=channel_name
                )
            )
