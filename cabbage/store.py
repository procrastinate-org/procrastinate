import inspect
import logging
from typing import Iterable, Iterator, Optional, Any

from cabbage import exceptions, jobs, metadata

logger = logging.getLogger(__name__)


def load_store(name: str, **kwargs: Any) -> "JobStore":
    job_store_eps = metadata.entrypoints("cabbage.job_store")

    candidates = [ep for ep in job_store_eps if ep.name == name]

    if len(candidates) > 1:
        stores = ", ".join(ep.value for ep in candidates)
        logger.warning(f"More than one store found with name {name}: {stores}.")

    if candidates:
        ep = candidates[0]
        logger.info(f"Selecting store {name} ({ep.value})")
        cls = ep.load()

        if not inspect.isclass(cls) or not issubclass(cls, JobStore):
            raise exceptions.JobStoreNotFound(f"{ep.value} is not a JobStore subclass")

        # Let it crash if we don't have the right arguments
        return cls(**kwargs)  # type: ignore

    raise exceptions.JobStoreNotFound(
        f"Found no cabbage.job_store entrypoint with name {name}"
    )


class JobStore:
    def launch_job(self, job: jobs.Job) -> int:
        raise NotImplementedError

    def get_jobs(self, queues: Optional[Iterable[str]]) -> Iterator[jobs.Job]:
        raise NotImplementedError

    def finish_job(self, job: jobs.Job, status: jobs.Status) -> None:
        raise NotImplementedError

    def listen_for_jobs(self, queues: Optional[Iterable[str]] = None) -> None:
        raise NotImplementedError

    def wait_for_jobs(self, timeout: float):
        raise NotImplementedError
