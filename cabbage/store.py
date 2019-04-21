from typing import Iterator, Optional

from cabbage import jobs, types


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
