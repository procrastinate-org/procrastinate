import logging
import uuid
from typing import Any, Callable, Dict, Iterator, Optional, Set

from cabbage import postgres, types

logger = logging.getLogger(__name__)


class Task:
    def __init__(
        self, *, manager: "TaskManager", queue: str, name: Optional[str] = None
    ):
        self.queue = queue
        self.manager = manager
        self.func: Optional[Callable] = None
        self.name = name

    def __call__(self, func: Callable) -> "Task":
        self.func = func
        if not self.name:
            self.name = func.__name__
        self.manager.register(self)
        return self

    def defer(self, lock: str = None, **kwargs: types.JSONValue) -> None:
        lock = lock or f"{uuid.uuid4()}"
        logger.info(
            f"Scheduling task {self.name} in queue {self.queue} with args {kwargs}"
        )
        assert self.name, "Task has no name"
        postgres.launch_task(
            self.manager.connection,
            queue=self.queue,
            name=self.name,
            lock=lock,
            kwargs=kwargs,
        )


class TaskManager:
    def __init__(self, connection: Any = None) -> None:
        if connection is None:
            connection = postgres.get_connection()

        self.connection = connection
        self.tasks: Dict[str, Task] = {}
        self.queues: Set[str] = set()

    def task(self, **kwargs) -> Task:
        kwargs["manager"] = self
        task = Task(**kwargs)
        return task

    def register(self, task: Task) -> None:
        assert task.name, "Task has no name"
        self.tasks[task.name] = task
        if task.queue not in self.queues:
            logger.info(f"Creating queue {task.queue} (if not already existing)")
            postgres.register_queue(self.connection, task.queue)
            self.queues.add(task.queue)

    def get_tasks(self, queue: str) -> Iterator[postgres.TaskRow]:
        return postgres.get_tasks(self.connection, queue)

    def finish_task(self, task_row: postgres.TaskRow, status: str) -> None:
        return postgres.finish_task(self.connection, task_row.id, status)


class TaskRun:
    def __init__(
        self, task: Task, id: int, lock: str
    ):  # pylint: disable=redefined-builtin
        self.task = task
        self.id = id
        self.lock = lock

    def run(self, **kwargs) -> None:
        assert self.task.func, "Task has no associated function"
        self.task.func(self, **kwargs)
