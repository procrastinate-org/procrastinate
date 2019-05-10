import datetime
import functools
import logging
import uuid
from typing import Any, Callable, Dict, Optional, Set

import pendulum

from cabbage import exceptions, jobs, postgres, store, types, utils

logger = logging.getLogger(__name__)


def load_task(path: str) -> "Task":

    try:
        task = utils.load_from_path(path)
    except ImportError:
        raise exceptions.TaskNotFound(f"Task at {path} cannot be imported")

    if not isinstance(task, Task):
        raise exceptions.NotATask(f"Object at {path} is not a Task but: {type(task)}")

    return task


class Task:
    def __init__(
        self,
        func: Callable,
        *,
        manager: "TaskManager",
        queue: str,
        name: Optional[str] = None,
    ):
        self.queue = queue
        self.manager = manager
        self.func: Callable = func
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

    def __call__(self, **kwargs: types.JSONValue) -> None:
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
            job_store=self.manager.job_store,
        )


class TaskManager:
    def __init__(self, job_store: Optional[store.JobStore] = None):
        if job_store is None:
            job_store = postgres.PostgresJobStore()

        self.job_store = job_store
        self.tasks: Dict[str, Task] = {}
        self.queues: Set[str] = set()

    def task(
        self,
        _func: Optional[Callable] = None,
        queue: str = "default",
        name: Optional[str] = None,
    ) -> Callable:
        """
        Declare a function as a task.

        Can be used as a decorator or a simple method.
        """

        def _wrap(func: Callable) -> Callable[..., Any]:
            task = Task(func, manager=self, queue=queue, name=name)
            self.register(task)

            return functools.update_wrapper(task, func)

        if _func is None:
            return _wrap

        return _wrap(_func)

    def register(self, task: Task) -> None:
        self.tasks[task.name] = task
        if task.queue not in self.queues:
            logger.info(
                "Creating queue (if not already existing)",
                extra={"action": "create_queue", "queue": task.queue},
            )
            self.job_store.register_queue(task.queue)
            self.queues.add(task.queue)
