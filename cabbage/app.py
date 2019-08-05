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

    def __init__(self, job_store: Optional[store.JobStore] = None):
        """
        Parameters
        ----------
        job_store:
            The object in charge of :py:class:`cabbage.jobs.Job` persistance.
            By default, instanciate a :py:class:`cabbage.PostgresJobStore`.

        Returns
        -------
        App
        """
        if job_store is None:
            job_store = postgres.PostgresJobStore()

        self.job_store = job_store
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
