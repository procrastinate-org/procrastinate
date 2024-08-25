from __future__ import annotations

import time
from typing import Any, Callable, Iterable

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
    """

    #: Procrastinate `App` running this job
    app: app_module.App
    #: Name of the worker (may be useful for logging)
    worker_name: str | None = None
    #: Queues listened by this worker
    worker_queues: Iterable[str] | None = None
    #: Corresponding :py:class:`~jobs.Job`
    job: jobs.Job
    #: Corresponding :py:class:`~tasks.Task`
    task: tasks.Task | None = None
    job_result: JobResult = attr.ib(factory=JobResult)
    additional_context: dict = attr.ib(factory=dict)
    task_result: Any = None

    should_abort: Callable[[], bool]

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
