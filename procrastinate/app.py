import functools
import logging
import warnings
from typing import TYPE_CHECKING, Any, Callable, Dict, Iterable, Optional, Set

from procrastinate import builtin_tasks
from procrastinate import connector as connector_module
from procrastinate import exceptions, healthchecks, jobs
from procrastinate import retry as retry_module
from procrastinate import schema, store, utils

if TYPE_CHECKING:
    from procrastinate import tasks, worker

logger = logging.getLogger(__name__)


@utils.add_sync_api
class App:
    """
    The App is the main entry point for procrastinate integration.

    Instantiate a single :py:class:`App` in your code
    and use it to decorate your tasks with :py:func:`App.task`.

    You can run a worker with :py:func:`App.run_worker`.
    """

    @classmethod
    def from_path(cls, dotted_path: str):
        return utils.load_from_path(dotted_path, cls)

    def __init__(
        self,
        *,
        connector: Optional[connector_module.BaseConnector] = None,
        import_paths: Optional[Iterable[str]] = None,
        # Just for backwards compatibility
        job_store: Optional[connector_module.BaseConnector] = None,
    ):
        """
        Parameters
        ----------
        connector:
            Instance of a subclass of :py:class:`BaseConnector`, typically
            :py:class:`PostgresConnector`. It will be responsible for all
            communications with the database.
            Mandatory if job_store is not passed.
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
        job_store:
            **Deprecated**: Old name of ``connector``.
        """
        # Compatibility
        if job_store:
            message = (
                "Use App(connector=procrastinate.PostgresConnector(...)) "
                "instead of App(job_store=procrastinate.PostgresJobStore())"
            )
            logger.warn(f"Deprecation Warning: {message}")
            warnings.warn(DeprecationWarning(message))
            connector = job_store
        if not connector:
            raise TypeError("App() missing 1 required argument: 'connector'")

        self.connector = connector
        self.tasks: Dict[str, "tasks.Task"] = {}
        self.builtin_tasks: Dict[str, "tasks.Task"] = {}
        self.queues: Set[str] = set()
        self.import_paths = import_paths or []

        self.job_store = store.JobStore(connector=self.connector)

        self._register_builtin_tasks()

    def task(
        self,
        _func: Optional[Callable] = None,
        *,
        queue: str = jobs.DEFAULT_QUEUE,
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
        queue = task.queue
        if queue not in self.queues:
            logger.debug(
                f"Registering queue {queue}",
                extra={"action": "register_queue", "queue": queue},
            )
            self.queues.add(queue)

    def _register_builtin_tasks(self) -> None:
        builtin_tasks.register_builtin_tasks(self)

    def configure_task(self, name: str, **kwargs: Any) -> jobs.JobDeferrer:
        """
        Configure a task for deferring, using its name

        Parameters
        ----------
        name : str
            Name of the task. If not explicitly defined, this will be the dotted path
            to the task (``my.module.my_task``)

        **kwargs: Any
            Parameters from :py:func:`Task.configure`

        Returns
        -------
        ``jobs.JobDeferrer``
            Launch ``.defer(**task_kwargs)`` on this object to defer your job.
        """
        from procrastinate import tasks

        return tasks.configure_task(name=name, job_store=self.job_store, **kwargs)

    def _worker(
        self, queues: Optional[Iterable[str]] = None, name: Optional[str] = None
    ) -> "worker.Worker":
        from procrastinate import worker

        return worker.Worker(app=self, queues=queues, name=name)

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

    async def run_worker_async(
        self,
        queues: Optional[Iterable[str]] = None,
        name: Optional[str] = None,
        only_once: bool = False,
    ) -> None:
        """
        Run a worker. This worker will run in the foreground
        and the function will not return until the worker stops
        (most probably when it receives a stop signal) (except if
        `only_once` is True).

        Parameters
        ----------
        queues:
            List of queues to listen to, or None to listen to
            every queue.
        only_once:
            If True, the worker will run but just for the currently
            defined tasks. This function will return when the
            listened queues are empty.
        """
        worker = self._worker(queues=queues, name=name)
        if only_once:
            try:
                await worker.process_jobs_once()
            except (exceptions.NoMoreJobs, exceptions.StopRequested):
                pass
        else:
            await worker.run()

    @property
    def schema_manager(self) -> schema.SchemaManager:
        return schema.SchemaManager(connector=self.connector)

    @property
    def health_check_runner(self) -> healthchecks.HealthCheckRunner:
        return healthchecks.HealthCheckRunner(connector=self.connector)

    async def close_connection_async(self):
        await self.connector.close_connection()
