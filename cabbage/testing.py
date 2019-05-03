from itertools import count
from typing import Dict, Iterator, List, Optional

from cabbage import jobs, store


class InMemoryJobStore(store.JobStore):
    def __init__(self):
        self.jobs: Dict[str, List[jobs.Job]] = {}
        self.queues_counter = count()
        self.job_counter = count()
        self.listening_queues = set()
        self.waited = []
        self.finished_jobs = []

    def register_queue(self, queue: str) -> Optional[int]:
        self.jobs[queue] = []
        return next(self.queues_counter)

    def launch_job(self, job: jobs.Job) -> int:
        id = next(self.job_counter)
        self.jobs[job.queue].append(
            jobs.Job(
                id=id,
                task_name=job.task_name,
                lock=job.lock,
                task_kwargs=job.task_kwargs,
                queue=job.queue,
                job_store=self,
            )
        )
        return id

    def get_jobs(self, queue: str) -> Iterator[jobs.Job]:
        for job in list(self.jobs[queue]):
            yield job

    def finish_job(self, job: jobs.Job, status: jobs.Status) -> None:
        j = self.jobs[job.queue].pop(0)
        assert job == j, (job, j)
        self.finished_jobs.append((job, status))

    def listen_for_jobs(self, queue: str):
        self.listening_queues.add(queue)

    def wait_for_jobs(self, timeout: int):
        self.waited.append(timeout)
