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
    job : `Job`
        Current `Job` instance
    task : `Task`
        Current `Task` instance
    """

    app: Optional[app_module.App] = None
    worker_name: Optional[str] = None
    worker_queues: Optional[Iterable[str]] = None
    job: Optional[jobs.Job] = None
    task: Optional[tasks.Task] = None
    additional_context: Dict = attr.ib(factory=dict)

    def log_extra(self, action: str, **kwargs: Any) -> types.JSONDict:
        extra: types.JSONDict = {
            "action": action,
            "worker": {"name": self.worker_name, "queues": self.worker_queues},
        }
        if self.job:
            extra["job"] = self.job.log_context()

        return {**extra, **self.additional_context, **kwargs}

    def evolve(self, **update) -> "JobContext":
        return attr.evolve(self, **update)

    @property
    def queues_display(self):
        if self.worker_queues:
            return f"queues {', '.join(self.worker_queues)}"
        else:
            return "all queues"
