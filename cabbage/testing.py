from collections import defaultdict
from itertools import count
from typing import DefaultDict, Dict, Iterator, List, Optional

import attr
import pendulum

from cabbage import jobs, store


class InMemoryJobStore(store.JobStore):
    def __init__(self):
        self.jobs: DefaultDict[str, List[jobs.Job]] = defaultdict(list)
        self.queues_counter = count()
        self.job_counter = count()
        self.listening_queues = set()
        self.waited = []
        self.finished_jobs = []

    def launch_job(self, job: jobs.Job) -> int:
        id = next(self.job_counter)
        self.jobs[job.queue].append(attr.evolve(job, id=id))

        return id

    def get_jobs(self, queue: str) -> Iterator[jobs.Job]:
        # Creating a copy of the iterable so that we can modify it while we iterate

        for job in list(self.jobs[queue]):
            if not job.scheduled_at or job.scheduled_at <= pendulum.now("UTC"):
                yield job

    def finish_job(self, job: jobs.Job, status: jobs.Status) -> None:
        j = self.jobs[job.queue].pop(0)
        assert job == j, (job, j)
        self.finished_jobs.append((job, status))

    def listen_for_jobs(self, queue: str):
        self.listening_queues.add(queue)

    def wait_for_jobs(self, timeout: int):
        self.waited.append(timeout)
