from typing import Any, Dict, Iterable, Optional

import attr

from procrastinate import app as app_module
from procrastinate import jobs, tasks, types


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

    app: Optional[app_module.App] = None
    worker_name: Optional[str] = None
    worker_queues: Optional[Iterable[str]] = None
    worker_id: Optional[int] = None
    job: Optional[jobs.Job] = None
    task: Optional[tasks.Task] = None
    additional_context: Dict = attr.ib(factory=dict)

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

        return {**extra, **self.additional_context, **kwargs}

    def evolve(self, **update: Any) -> "JobContext":
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
            start = self.additional_context.get("start_timestamp")
            if start:
                assert isinstance(start, float)
                ago = current_timestamp - start
                message += f" (started {ago:.3f} s ago)"
        else:
            message += "no current job"

        return message
