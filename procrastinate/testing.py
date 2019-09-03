import datetime
from itertools import count
from typing import Iterable, List, Optional, Set, Tuple

import attr
import pendulum

from procrastinate import jobs, store


class InMemoryJobStore(store.BaseJobStore):
    """
    An InMemoryJobStore may be used for testing only. Tasks are not
    persisted and will be lost when the process ends.

    While implementing the JobStore interface, it also adds a few
    methods and attributes to ease testing.
    """

    def __init__(self):
        """
        Attributes
        ----------
        jobs : List[jobs.Job]
            Currently running Job objects. They are removed from this
            list upon completion
        finished_jobs: List[Tuple[jobs.Job, jobs.Status]]
            List of finished jobs, with their related status
        """
        self.reset()

    def reset(self):
        """
        Removes anything the store contains, to ensure test independance.
        """
        self.jobs: List[jobs.Job] = []
        self.current_job_ids: Set[int] = set()
        self.finished_jobs: List[Tuple[jobs.Job, jobs.Status]] = []
        self.job_counter = count(1)
        self.listening_queues: Set[str] = set()
        self.listening_all_queues = False
        self.waited = False
        self.queries = []

    def launch_job(self, job: jobs.Job) -> int:
        id = next(self.job_counter)
        self.jobs.append(attr.evolve(job, id=id))

        return id

    @property
    def current_locks(self) -> Iterable[str]:
        return {job.lock for job in self.jobs if job.id in self.current_job_ids}

    def get_job(self, queues: Optional[Iterable[str]]) -> Optional[jobs.Job]:
        # Creating a copy of the iterable so that we can modify it while we iterate

        for job in self.jobs:
            if queues is None or job.queue in queues:
                if (
                    (not job.scheduled_at or job.scheduled_at <= pendulum.now("UTC"))
                    and job.id not in self.current_job_ids
                    and job.lock not in self.current_locks
                ):
                    self.current_job_ids.add(job.id or 0)
                    return job
        return None

    def finish_job(
        self,
        job: jobs.Job,
        status: jobs.Status,
        scheduled_at: Optional[datetime.datetime] = None,
    ) -> None:
        self.jobs.remove(job)
        self.current_job_ids.remove(job.id or 0)
        if status in [jobs.Status.SUCCEEDED, jobs.Status.FAILED]:
            self.finished_jobs.append((job, status))
        else:
            self.jobs.append(
                attr.evolve(job, attempts=job.attempts + 1, scheduled_at=scheduled_at)
            )

    def listen_for_jobs(self, queues: Optional[Iterable[str]] = None) -> None:
        if queues is None:
            self.listening_all_queues = True
        else:
            self.listening_queues.update(queues)

    def wait_for_jobs(self):
        self.waited = True

    def stop(self):
        pass

    def execute_queries(self, queries: str):
        self.queries.append(queries)
