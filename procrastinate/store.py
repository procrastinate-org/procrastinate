import datetime
from typing import Iterable, Optional

from procrastinate import jobs, types


class BaseJobStore:
    def defer_job(self, job: jobs.Job) -> int:
        raise NotImplementedError

    def get_job(self, queues: Optional[Iterable[str]]) -> Optional[jobs.Job]:
        raise NotImplementedError

    def delete_old_jobs(
        self,
        nb_hours: int,
        queue: Optional[str] = None,
        include_error: Optional[bool] = False,
    ) -> None:
        raise NotImplementedError

    def finish_job(
        self,
        job: jobs.Job,
        status: jobs.Status,
        scheduled_at: Optional[datetime.datetime] = None,
    ) -> None:
        raise NotImplementedError

    def listen_for_jobs(self, queues: Optional[Iterable[str]] = None) -> None:
        raise NotImplementedError

    def wait_for_jobs(self):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError

    def get_connection(self) -> types.Connection:
        raise NotImplementedError

    def execute_queries(self, queries: str):
        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(queries)
