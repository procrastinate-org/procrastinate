from typing import Iterator, Optional, Type

from cabbage import jobs, utils


def load_store_from_path(path: str) -> Type["JobStore"]:
    """
    Import the JobStore subclass at the given path, return the class.
    """
    job_store_class = utils.load_from_path(path, type)

    assert issubclass(job_store_class, JobStore)

    return job_store_class


class JobStore:
    def launch_job(self, job: jobs.Job) -> int:
        raise NotImplementedError

    def get_jobs(self, queue: str) -> Iterator[jobs.Job]:
        raise NotImplementedError

    def finish_job(self, job: jobs.Job, status: jobs.Status) -> None:
        raise NotImplementedError

    def listen_for_jobs(self, queue: str):
        raise NotImplementedError

    def wait_for_jobs(self, timeout: int):
        raise NotImplementedError
