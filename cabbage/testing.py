from itertools import count
from typing import Iterable, Iterator, List, Optional, Tuple

import attr
import pendulum

from cabbage import jobs, store


class InMemoryJobStore(store.JobStore):
    def __init__(self):
        self.jobs: List[jobs.Job] = []
        self.finished_jobs: List[Tuple[jobs.Job, jobs.Status]] = []
        self.queues_counter = count()
        self.job_counter = count()
        self.listening_queues = set()
        self.listening_all_queues = False
        self.waited = []

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

    def finish_job(self, job: jobs.Job, status: jobs.Status) -> None:
        self.jobs.remove(job)
        self.finished_jobs.append((job, status))

    def listen_for_jobs(self, queues: Optional[Iterable[str]] = None) -> None:
        if queues is None:
            self.listening_all_queues = True
        else:
            self.listening_queues.update(queues)

    def wait_for_jobs(self, timeout: int):
        self.waited.append(timeout)
