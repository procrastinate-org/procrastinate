import datetime
from typing import Iterable, Iterator, Optional

from procrastinate import jobs


class BaseJobStore:
    def launch_job(self, job: jobs.Job) -> int:
        raise NotImplementedError

    def get_jobs(self, queues: Optional[Iterable[str]]) -> Iterator[jobs.Job]:
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
