from __future__ import annotations

import time
from typing import Any, Iterable

import attr

from procrastinate import app as app_module
from procrastinate import jobs, tasks, types


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
    In theory, all attributes are optional. In practice, in a task, they will
    always be set to their proper value.

    Attributes
    ----------
    app : `App`
        Procrastinate `App` running this job
    worker_name : ``str``
        Name of the worker (may be useful for logging)
    worker_queues : ``Optional[Iterable[str]]``
        Queues listened by this worker
    worker_id : ``int```
        In case there are multiple async sub-workers, this is the id of the sub-worker.
    job : `Job`
        Current `Job` instance
    task : `Task`
        Current `Task` instance
    """

    app: app_module.App | None = None
    worker_name: str | None = None
    worker_queues: Iterable[str] | None = None
    worker_id: int | None = None
    job: jobs.Job | None = None
    task: tasks.Task | None = None
    job_result: JobResult = attr.ib(factory=JobResult)
    additional_context: dict = attr.ib(factory=dict)

    def log_extra(self, action: str, **kwargs: Any) -> types.JSONDict:
        extra: types.JSONDict = {
            "action": action,
            "worker": {
                "name": self.worker_name,
                "id": self.worker_id,
                "queues": self.worker_queues,
            },
        }
        if self.job:
            extra["job"] = self.job.log_context()

        return {**extra, **self.job_result.as_dict(), **kwargs}

    def evolve(self, **update: Any) -> JobContext:
        return attr.evolve(self, **update)

    @property
    def queues_display(self) -> str:
        if self.worker_queues:
            return f"queues {', '.join(self.worker_queues)}"
        else:
            return "all queues"

    def job_description(self, current_timestamp: float) -> str:
        message = f"worker {self.worker_id}: "
        if self.job:
            message += self.job.call_string
            duration = self.job_result.duration(current_timestamp)
            if duration is not None:
                message += f" (started {duration:.3f} s ago)"
        else:
            message += "no current job"

        return message
