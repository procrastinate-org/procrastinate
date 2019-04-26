import importlib
from typing import Iterator, Optional, Type

from cabbage import jobs, types


def load_store_from_path(path: str) -> Type["JobStore"]:
    """
    Import the JobStore subclass at the given path, return the class.
    """
    path, name = path.rsplit(".", 1)
    module = importlib.import_module(path)

    job_store_class = getattr(module, name)

    assert issubclass(job_store_class, JobStore)

    return job_store_class


class JobStore:
    def register_queue(self, queue: str) -> Optional[int]:
        raise NotImplementedError

    def launch_task(
        self, queue: str, name: str, lock: str, kwargs: types.JSONDict
    ) -> int:
        raise NotImplementedError

    def get_tasks(self, queue: str) -> Iterator[jobs.Job]:
        raise NotImplementedError

    def finish_task(self, job: jobs.Job, status: jobs.Status) -> None:
        raise NotImplementedError

    def listen_for_jobs(self, queue: str):
        raise NotImplementedError

    def wait_for_jobs(self, timeout: int):
        raise NotImplementedError
