import functools
import logging
from typing import Any, Callable, Dict, Iterable, Optional, Set

from cabbage import postgres
from cabbage import retry as retry_module
from cabbage import store, tasks, testing, worker

logger = logging.getLogger(__name__)


class App:
    """
    The App is the main entrypoint for Cabbage integration.

    Instanciate a single :py:class:`App` in your code
    and use it to decorate your tasks with :py:func:`App.task`.

    You can run a worker with :py:func:`App.run_worker`.
    """

    def __init__(
        self,
        *,
        postgres_dsn: str = "",
        import_paths: Optional[Iterable[str]] = None,
        in_memory: bool = False,
        worker_timeout: float = worker.SOCKET_TIMEOUT,
    ):
        """
        Parameters
        ----------
        postgres_dsn:
            postgres (libpq) compatible connection string. See specications:
            https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING
        in_memory:
            If True, tasks will not be persisted. This is useful for testing only.
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
        worker_timeout:
            This parameter should generally not be changed.
            It indicates how long cabbage waits (in seconds) between
            renewing the socket `select` calls when waiting for tasks.
            The shorter the timeout, the more `select` calls it does.
            The longer the timeout, the longer the server will wait idle if, for
            some reason, the postgres LISTEN call doesn't work.
        """
        self.job_store: store.JobStore

        if in_memory:
            self.job_store = testing.InMemoryJobStore()
        else:
            connection = postgres.get_connection(dsn=postgres_dsn)
            self.job_store = postgres.PostgresJobStore(connection=connection)

        self.tasks: Dict[str, tasks.Task] = {}
        self.queues: Set[str] = set()
        self.import_paths = import_paths
        self.worker_timeout = worker_timeout

    def task(
        self,
        _func: Optional[Callable] = None,
        queue: str = "default",
        name: Optional[str] = None,
        retry: retry_module.RetryValue = False,
    ) -> Callable:
        """
        Declare a function as a task.

        Can be used as a decorator or a simple method.
        """

        def _wrap(func: Callable) -> Callable[..., Any]:
            task = tasks.Task(func, app=self, queue=queue, name=name, retry=retry)
            self._register(task)

            return functools.update_wrapper(task, func)

        if _func is None:
            return _wrap

        return _wrap(_func)

    def _register(self, task: tasks.Task) -> None:
        self.tasks[task.name] = task
        if task.queue not in self.queues:
            logger.debug(
                "Registering queue",
                extra={"action": "register_queue", "queue": task.queue},
            )
            self.queues.add(task.queue)

    def _worker(self, queues: Optional[Iterable[str]] = None) -> worker.Worker:
        return worker.Worker(app=self, queues=queues, import_paths=self.import_paths)

    def run_worker(
        self, queues: Optional[Iterable[str]] = None, only_once: bool = False
    ) -> None:
        """
        Run a worker. This worker will run in the foreground
        and the function will not return until the worker stops
        (most probably when it recieves a stop signal) (except if
        `only_once` is True)

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
            worker.run(timeout=self.worker_timeout)
