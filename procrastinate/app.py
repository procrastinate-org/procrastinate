import functools
import logging
from typing import TYPE_CHECKING, Any, Callable, Dict, Iterable, Optional, Set

from procrastinate import builtin_tasks, migration
from procrastinate import retry as retry_module
from procrastinate import store, utils

if TYPE_CHECKING:
    from procrastinate import tasks, worker

logger = logging.getLogger(__name__)


class App:
    """
    The App is the main entrypoint for procrastinate integration.

    Instanciate a single :py:class:`App` in your code
    and use it to decorate your tasks with :py:func:`App.task`.

    You can run a worker with :py:func:`App.run_worker`.
    """

    @classmethod
    def from_path(cls, dotted_path: str):
        return utils.load_from_path(dotted_path, cls)

    def __init__(
        self,
        *,
        job_store: store.BaseJobStore,
        import_paths: Optional[Iterable[str]] = None,
    ):
        """
        Parameters
        ----------
        job_store:
            Instance of a subclass of :py:class:`BaseJobStore`, typically
            :py:class:`PostgresJobStore`. It will be responsible for all
            communications with the database.
        import_paths:
            List of python dotted paths of modules to import, to make sure
            that the workers know about all possible tasks.
            If you fail to add a path here and a worker encounters
            a task defined at that path, the task will be loaded on the
            fly and run, but you will get a warning.
            You don't need to specify paths that you know have already
            been imported, though it doesn't hurt.
            A :py:func:`App.task` that has a custom "name" parameter, that is not
            imported and whose module path is not in this list will
            fail to run.
        """
        self.job_store = job_store
        self.tasks: Dict[str, "tasks.Task"] = {}
        self.builtin_tasks: Dict[str, "tasks.Task"] = {}
        self.queues: Set[str] = set()
        self.import_paths = import_paths or []

        self._register_builtin_tasks()

    def task(
        self,
        _func: Optional[Callable] = None,
        *,
        queue: str = "default",
        name: Optional[str] = None,
        retry: retry_module.RetryValue = False,
    ) -> Any:
        """
        Declare a function as a task. This method is meant to be used as a decorator::

            @app.task(...)
            def my_task(args):
                ...

        or::

            @app.task
            def my_task(args):
                ...

        The second form will use the default value for all parameters.

        Parameters
        ----------
        _func :
            The decorated function
        queue :
            The name of the queue in which jobs from this task will be launched, if
            the queue is not overridden at launch.
            Default is ``"default"``.
            When a worker is launched, it can listen to specific queues, or to all
            queues.
        name :
            Name of the task, by default the full dotted path to the decorated function.
            if the function is nested or dynamically defined, it is important to give
            it a unique name, and to make sure the module that defines this function
            is listed in the ``import_paths`` of the :py:class:`procrastinate.App`.
        retry :
            Details how to auto-retry the task if it fails. Can be:

            - A ``boolean``: will either not retry or retry indefinitely
            - An ``int``: the number of retries before it gives up
            - A :py:class:`procrastinate.RetryStrategy` instance for complex cases

            Default is no retry.
        """
        # Because of https://github.com/python/mypy/issues/3157, this function
        # is quite impossible to type consistently, so, we're just using "Any"

        def _wrap(func: Callable[..., "tasks.Task"]):
            from procrastinate import tasks

            task = tasks.Task(func, app=self, queue=queue, name=name, retry=retry)
            self._register(task)

            return functools.update_wrapper(task, func)

        if _func is None:  # Called as @app.task(...)
            return _wrap

        return _wrap(_func)  # Called as @app.task

    def _register(self, task: "tasks.Task") -> None:
        self.tasks[task.name] = task
        if task.queue not in self.queues:
            logger.debug(
                "Registering queue",
                extra={"action": "register_queue", "queue": task.queue},
            )
            self.queues.add(task.queue)

    def _register_builtin_tasks(self) -> None:
        builtin_tasks.register_builtin_tasks(self)

    def _worker(self, queues: Optional[Iterable[str]] = None) -> "worker.Worker":
        from procrastinate import worker

        return worker.Worker(app=self, queues=queues)

    @functools.lru_cache(maxsize=1)
    def perform_import_paths(self):
        """
        Whenever using app.tasks, make sure the apps have been imported by calling
        this method.
        """
        utils.import_all(import_paths=self.import_paths)
        logger.debug(
            "All tasks imported",
            extra={"action": "imported_tasks", "tasks": list(self.tasks)},
        )

    def run_worker(
        self, queues: Optional[Iterable[str]] = None, only_once: bool = False
    ) -> None:
        """
        Run a worker. This worker will run in the foreground
        and the function will not return until the worker stops
        (most probably when it recieves a stop signal) (except if
        `only_once` is True).

        Parameters
        ----------
        queues:
            List of queues to listen to, or None to listen to
            every queue.
        only_once:
            If True, the worker will rune but just for the currently
            defined tasks. This function will return when the
            listened queues are empty.
        """
        worker = self._worker(queues=queues)
        if only_once:
            worker.process_jobs_once()
        else:
            worker.run()

    @property
    def migrator(self) -> migration.Migrator:
        return migration.Migrator(job_store=self.job_store)
