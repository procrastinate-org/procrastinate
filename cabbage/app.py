import functools
import logging
from typing import Any, Callable, Dict, Optional, Set

from cabbage import postgres, store, tasks

logger = logging.getLogger(__name__)


class App:
    """
    The App is the main entrypoint for Cabbage integration.

    Instanciate a single :py:class:`App` in your code
    and use it to decorate your tasks with :py:func:`App.task`.

    Yada yada instanciate worker from app yada yada

    """

    def __init__(
        self,
        *,
        postgres_dsn: str = "",
        in_memory: bool = False
    ):
        """
        Parameters
        ----------
        postgres_dsn:
            postgres (libpq) compatible connection string. See specications:
            https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING
        in_memory:
            If True, tasks will not be persisted. This is useful for testing only.
        """
        self.job_store: store.JobStore

        if in_memory:
            self.job_store = testing.InMemoryJobStore()
        else:
            connection = postgres.get_connection(dsn=postgres_dsn)
            self.job_store = postgres.PostgresJobStore(connection=connection)

        self.tasks: Dict[str, tasks.Task] = {}
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
            task = tasks.Task(func, app=self, queue=queue, name=name)
            self.register(task)

            return functools.update_wrapper(task, func)

        if _func is None:
            return _wrap

        return _wrap(_func)

    def register(self, task: tasks.Task) -> None:
        self.tasks[task.name] = task
        if task.queue not in self.queues:
            logger.info(
                "Creating queue (if not already existing)",
                extra={"action": "create_queue", "queue": task.queue},
            )
            self.queues.add(task.queue)
