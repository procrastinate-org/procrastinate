import functools
import logging
from typing import TYPE_CHECKING, Any, Dict, Iterable, Optional, Union

from procrastinate import blueprints
from procrastinate import connector as connector_module
from procrastinate import exceptions, jobs, manager, schema, utils

if TYPE_CHECKING:
    from procrastinate import worker

logger = logging.getLogger(__name__)


class App(blueprints.Blueprint):
    """
    The App is the main entry point for procrastinate integration.

    Instantiate a single `App` in your code
    and use it to decorate your tasks with `App.task`.

    You can run a worker with `App.run_worker`.

    Attributes
    ----------
    tasks : ``Dict[str, tasks.Task]``
        The mapping of all tasks known by the app. Only procrastinate is expected to
        make changes to this mapping.
    job_manager : `manager.JobManager`
        The `JobManager` linked to the application
    """

    @classmethod
    def from_path(cls, dotted_path: str) -> "App":
        """
        Create an :py:class:`App` object by dynamically loading the
        object at the given path.

        Parameters
        ----------
        dotted_path :
            Dotted path to the object to load (e.g.
            ``mymodule.submodule.procrastinate_app``)
        """
        return utils.load_from_path(dotted_path, cls)

    def __init__(
        self,
        *,
        connector: connector_module.BaseConnector,
        import_paths: Optional[Iterable[str]] = None,
        worker_defaults: Optional[Dict] = None,
        periodic_defaults: Optional[Dict] = None,
    ):
        """
        Parameters
        ----------
        connector :
            Typically an `AiopgConnector`. It will be responsible for all communications
            with the database. Mandatory.
        import_paths :
            List of python dotted paths of modules to import, to make sure that
            the workers know about all possible tasks. If there are tasks in a
            module that is neither imported as a side effect of importing the
            App, nor specified in this list, and a worker encounters a task
            defined in that module, the task will fail (`TaskNotFound`). While
            it is not mandatory to specify paths to modules that you know have
            already been imported, it's a good idea to do so.
        worker_defaults :
            All the values passed here will override the default values sent when
            launching a worker. See `App.run_worker` for details.
        periodic_defaults :
            Parameters for fine tuning the periodic tasks deferrer. Available
            parameters are:

            - ``max_delay``: ``float``, in seconds. When a worker starts and there's
              a periodic task that has not been deferred, the worker will defer the task
              if it's been due for less that this amount of time. This avoids new
              periodic tasks to be immediately deferred just after their first
              deployment. (defaults to 10 minutes)
        """
        from procrastinate import periodic

        super().__init__()

        self.connector = connector
        self.import_paths = import_paths or []
        self.worker_defaults = worker_defaults or {}
        periodic_defaults = periodic_defaults or {}

        self.job_manager = manager.JobManager(connector=self.connector)
        self.periodic_deferrer = periodic.PeriodicDeferrer(**periodic_defaults)

        self._register_builtin_tasks()

    def with_connector(self, connector: connector_module.BaseConnector) -> "App":
        """
        Create another app instance sychronized with this one, with a different
        connector. For all things regarding periodic tasks, the original app
        (and its original connector) will be used, even when the new app's
        methods are used.

        Returns
        -------
        `App`
            A new compatible app.
        """
        app = App(
            connector=connector,
            import_paths=self.import_paths,
            worker_defaults=self.worker_defaults,
        )
        app.tasks = self.tasks
        app.periodic_deferrer = self.periodic_deferrer
        return app

    def periodic(self, *, cron: str, periodic_id: str = "", **kwargs: Dict[str, Any]):
        """
        Task decorator, marks task as being scheduled for periodic deferring (see
        `howto/cron`).

        Parameters
        ----------
        cron :
            Cron-like string. Optionally add a 6th column for seconds.
        periodic_id :
            Task name suffix. Used to distinct periodic tasks with different kwargs.
        **kwargs :
            Additional parameters are passed to `Task.configure`.
        """
        return self.periodic_deferrer.periodic_decorator(
            cron=cron, periodic_id=periodic_id, **kwargs
        )

    def _register_builtin_tasks(self) -> None:
        from procrastinate import builtin_tasks

        self.add_tasks_from(builtin_tasks.builtin, namespace="builtin")

        # New tasks will be "builtin:procrastinate.builtin_tasks.remove_old_jobs"
        # but for compatibility, we can keep the old name around.
        self.add_task_alias(
            task=builtin_tasks.remove_old_jobs,
            alias="procrastinate.builtin_tasks.remove_old_jobs",
        )

    def configure_task(
        self, name: str, *, allow_unknown: bool = True, **kwargs: Any
    ) -> jobs.JobDeferrer:
        """
        Configure a task for deferring, using its name

        Parameters
        ----------
        name : str
            Name of the task. If not explicitly defined, this will be the dotted path
            to the task (``my.module.my_task``)

        **kwargs: Any
            Parameters from `Task.configure`

        Returns
        -------
        ``jobs.JobDeferrer``
            Launch ``.defer(**task_kwargs)`` on this object to defer your job.
        """
        from procrastinate import tasks

        self.perform_import_paths()
        try:
            return self.tasks[name].configure(**kwargs)
        except KeyError as exc:
            if allow_unknown:
                return tasks.configure_task(
                    name=name, job_manager=self.job_manager, **kwargs
                )
            raise exceptions.TaskNotFound from exc

    def _worker(self, **kwargs) -> "worker.Worker":
        from procrastinate import worker

        final_kwargs = {**self.worker_defaults, **kwargs}

        return worker.Worker(app=self, **final_kwargs)

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

    async def run_worker_async(self, **kwargs) -> None:
        """
        Run a worker. This worker will run in the foreground and execute the jobs in the
        provided queues. If wait is True, the function will not
        return until the worker stops (most probably when it receives a stop signal).
        The default values of all parameters presented here can be overridden at the
        `App` level.

        Parameters
        ----------
        queues : ``Optional[Iterable[str]]``
            List of queues to listen to, or None to listen to every queue (defaults to
            ``None``).
        wait : ``bool``
            If False, the worker will terminate as soon as it has caught up with the
            queues. If True, the worker will work until it is stopped by a signal
            (``ctrl+c``, ``SIGINT``, ``SIGTERM``) (defaults to ``True``).
        concurrency : ``int``
            Indicates how many asynchronous jobs the worker can run in parallel.
            Do not use concurrency if you have synchronous blocking tasks.
            See `howto/concurrency` (defaults to ``1``).
        name : ``Optional[str]``
            Name of the worker. Will be passed in the `JobContext` and used in the
            logs (defaults to ``None`` which will result in the worker named
            ``worker``).
        timeout : ``float``
            Indicates the maximum duration (in seconds) the worker waits between
            each database job poll. Raising this parameter can lower the rate at which
            the worker makes queries to the database for requesting jobs.
            (defaults to 5.0)
        listen_notify : ``bool``
            If ``True``, the worker will dedicate a connection from the pool to
            listening to database events, notifying of newly available jobs.
            If ``False``, the worker will just poll the database periodically
            (see ``timeout``). (defaults to ``True``)
        delete_jobs : ``str``
            If ``always``, the worker will automatically delete all jobs on completion.
            If ``successful`` the worker will only delete successful jobs.
            If ``never``, the worker will keep the jobs in the database.
            (defaults to ``never``)
        additional_context: ``Optional[Dict[str, Any]]``
            If set extend the context received by the tasks when ``pass_context`` is set
            to ``True`` in the task definition.
        """
        self.perform_import_paths()
        worker = self._worker(**kwargs)
        await worker.run()

    async def check_connection_async(self):
        return await self.job_manager.check_connection()

    @property
    def schema_manager(self) -> schema.SchemaManager:
        return schema.SchemaManager(connector=self.connector)

    def open(
        self,
        pool_or_engine: Optional[
            Union[connector_module.Pool, connector_module.Engine]
        ] = None,
    ) -> "App":
        self.connector.open(pool_or_engine)
        return self

    def close(self) -> None:
        self.connector.close()

    def open_async(
        self, pool: Optional[connector_module.Pool] = None
    ) -> utils.AwaitableContext:
        open_coro = functools.partial(self.connector.open_async, pool=pool)
        return utils.AwaitableContext(
            open_coro=open_coro,
            close_coro=self.connector.close_async,
            return_value=self,
        )

    async def close_async(self) -> None:
        await self.connector.close_async()

    def __enter__(self) -> "App":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()


utils.add_method_sync_api(cls=App, method_name="run_worker_async")
utils.add_method_sync_api(cls=App, method_name="check_connection_async")
