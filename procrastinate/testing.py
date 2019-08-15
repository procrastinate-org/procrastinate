import datetime
from itertools import count
from typing import Iterable, Iterator, List, Optional, Set, Tuple

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
            List of finished jobs, with their associate status
        """
        self.reset()

    def reset(self):
        """
        Removes anything the store contains, to ensure test independance.
        """
        self.jobs: List[jobs.Job] = []
        self.finished_jobs: List[Tuple[jobs.Job, jobs.Status]] = []
        self.job_counter = count()
        self.listening_queues: Set[str] = set()
        self.listening_all_queues = False
        self.waited = False

    def launch_job(self, job: jobs.Job) -> int:
        id = next(self.job_counter)
        self.jobs.append(attr.evolve(job, id=id))

        return id

    def get_jobs(self, queues: Optional[Iterable[str]]) -> Iterator[jobs.Job]:
        # Creating a copy of the iterable so that we can modify it while we iterate

        for job in list(self.jobs):
            if queues is None or job.queue in queues:
                if not job.scheduled_at or job.scheduled_at <= pendulum.now("UTC"):
                    yield job

    def finish_job(
        self,
        job: jobs.Job,
        status: jobs.Status,
        scheduled_at: Optional[datetime.datetime] = None,
    ) -> None:
        self.jobs.remove(job)
        if status in [jobs.Status.DONE, jobs.Status.ERROR]:
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
