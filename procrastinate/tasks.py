import datetime
import logging
import uuid
from typing import TYPE_CHECKING, Any, Callable, Dict, Optional

import pendulum

from procrastinate import exceptions, jobs
from procrastinate import retry as retry_module
from procrastinate import types, utils

if TYPE_CHECKING:  # coverage: exclude
    from procrastinate import app

logger = logging.getLogger(__name__)


def load_task(path: str) -> "Task":
    try:
        task = utils.load_from_path(path, Task)
    except exceptions.LoadFromPathError as exc:
        raise exceptions.TaskNotFound(f"Task at {path} cannot be imported: {str(exc)}")

    return task


class Task:
    def __init__(
        self,
        func: Callable,
        *,
        app: "app.App",
        queue: str,
        name: Optional[str] = None,
        retry: retry_module.RetryValue = False,
    ):
        self.queue = queue
        self.app = app
        self.func: Callable = func
        self.retry_strategy = retry_module.get_retry_strategy(retry)
        self.name: str
        if name and name != self.full_path:
            logger.warning(
                f"Task {name} at {self.full_path} has a name that doesn't match "
                "its import path. Please make sure its module path is provided in "
                "the worker's import_paths, or it won't run.",
                extra={
                    "action": "task_name_differ_from_path",
                    "task_name": name,
                    "task_path": self.full_path,
                },
            )
            self.name = name
        else:
            self.name = self.full_path

    def __call__(self, **kwargs: types.JSONValue) -> Any:
        return self.func(**kwargs)

    @property
    def full_path(self) -> str:
        return f"{self.func.__module__}.{self.func.__name__}"

    def defer(self, **task_kwargs: types.JSONValue) -> int:
        job_id = self.configure().defer(**task_kwargs)

        return job_id

    def configure(
        self,
        *,
        lock: Optional[str] = None,
        task_kwargs: Optional[types.JSONDict] = None,
        schedule_at: Optional[datetime.datetime] = None,
        schedule_in: Optional[Dict[str, int]] = None,
    ) -> jobs.Job:
        if schedule_at and schedule_in is not None:
            raise ValueError("Cannot set both schedule_at and schedule_in")

        if schedule_in is not None:
            schedule_at = pendulum.now("UTC").add(**schedule_in)

        lock = lock or str(uuid.uuid4())
        task_kwargs = task_kwargs or {}
        return jobs.Job(
            id=None,
            lock=lock,
            task_name=self.name,
            queue=self.queue,
            task_kwargs=task_kwargs,
            scheduled_at=schedule_at,
            job_store=self.app.job_store,
        )

    def get_retry_exception(self, job: jobs.Job) -> Optional[exceptions.JobRetry]:
        if not self.retry_strategy:
            return None

        return self.retry_strategy.get_retry_exception(job.attempts)
