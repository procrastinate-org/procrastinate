from __future__ import annotations

import time
from typing import Any, Iterable

import attr

from procrastinate import app as app_module
from procrastinate import jobs, tasks, utils


@attr.dataclass(kw_only=True)
class JobResult:
    start_timestamp: float | None = None
    end_timestamp: float | None = None
    result: Any = None

    def duration(self, current_timestamp: float) -> float | None:
        if self.start_timestamp is None:
            return None
        return (self.end_timestamp or current_timestamp) - self.start_timestamp

    def as_dict(self):
        result = {}
        if self.start_timestamp:
            result.update(
                {
                    "start_timestamp": self.start_timestamp,
                    "duration": self.duration(current_timestamp=time.time()),
                }
            )
        if self.end_timestamp:
            result.update({"end_timestamp": self.end_timestamp, "result": self.result})
        return result


@attr.dataclass(frozen=True, kw_only=True)
class JobContext:
    """
    Execution context of a running job.


    Attributes
    ----------
    app : `App`
        Procrastinate `App` running this job
    worker_name : ``str``
        Name of the worker (may be useful for logging)
    worker_queues : ``Optional[Iterable[str]]``
        Queues listened by this worker
    job : `Job`
        Current `Job` instance
    task : `Task`
        Current `Task` instance. This can be None when the a task cannot be found for a given job.
        Any task function being called with a job context can be guaranteed to have its own task instance set.
    """

    app: app_module.App
    worker_name: str | None = None
    worker_queues: Iterable[str] | None = None
    job: jobs.Job
    task: tasks.Task | None = None
    job_result: JobResult = attr.ib(factory=JobResult)
    additional_context: dict = attr.ib(factory=dict)
    task_result: Any = None

    def evolve(self, **update: Any) -> JobContext:
        return attr.evolve(self, **update)

    @property
    def queues_display(self) -> str:
        return utils.queues_display(self.worker_queues)

    def job_description(self, current_timestamp: float) -> str:
        message = f"worker: {self.job.call_string}"
        duration = self.job_result.duration(current_timestamp)
        if duration is not None:
            message += f" (started {duration:.3f} s ago)"

        return message

    def should_abort(self) -> bool:
        assert self.job.id
        job_id = self.job.id
        return self.app.job_manager.get_job_abort_requested(job_id)

    async def should_abort_async(self) -> bool:
        assert self.job.id
        job_id = self.job.id
        return await self.app.job_manager.get_job_abort_requested_async(job_id)
