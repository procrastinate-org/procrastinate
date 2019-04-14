import logging
import uuid
from typing import Any, Callable, Dict, Iterator, Optional, Set

from cabbage import postgres, types

logger = logging.getLogger(__name__)


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
        self.name = name or self.func.__name__

    def __call__(self, **kwargs: types.JSONValue) -> None:
        return self.func(**kwargs)

    def defer(self, lock: str = None, **kwargs: types.JSONValue) -> None:
        lock = lock or f"{uuid.uuid4()}"
        task_id = postgres.launch_task(
            self.manager.connection,
            queue=self.queue,
            name=self.name,
            lock=lock,
            kwargs=kwargs,
        )
        logger.info(
            "Scheduled task",
            extra={
                "action": "task_defer",
                "name": self.name,
                "queue": self.queue,
                "kwargs": kwargs,
                "id": task_id,
            },
        )


class TaskManager:
    def __init__(self, connection: Any = None) -> None:
        if connection is None:
            connection = postgres.get_connection()

        self.connection = connection
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

        def _wrap(func: Callable) -> Task:
            task = Task(func, manager=self, queue=queue, name=name)
            self.register(task)

            return task

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
            postgres.register_queue(self.connection, task.queue)
            self.queues.add(task.queue)

    def get_tasks(self, queue: str) -> Iterator[postgres.TaskRow]:
        return postgres.get_tasks(self.connection, queue)

    def finish_task(self, task_row: postgres.TaskRow, status: str) -> None:
        return postgres.finish_task(self.connection, task_row.id, status)
