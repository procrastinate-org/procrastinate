import datetime
import logging
from typing import Any, Callable, Dict, List, Optional

from procrastinate import app as app_module
from procrastinate import blueprints, exceptions, jobs, manager
from procrastinate import retry as retry_module
from procrastinate import types, utils

logger = logging.getLogger(__name__)


def configure_task(
    *,
    name: str,
    job_manager: manager.JobManager,
    lock: Optional[str] = None,
    queueing_lock: Optional[str] = None,
    task_kwargs: Optional[types.JSONDict] = None,
    schedule_at: Optional[datetime.datetime] = None,
    schedule_in: Optional[Dict[str, int]] = None,
    queue: str = jobs.DEFAULT_QUEUE,
) -> jobs.JobDeferrer:
    if schedule_at and schedule_in is not None:
        raise ValueError("Cannot set both schedule_at and schedule_in")

    if schedule_in is not None:
        schedule_at = utils.utcnow() + datetime.timedelta(**schedule_in)

    task_kwargs = task_kwargs or {}
    return jobs.JobDeferrer(
        job=jobs.Job(
            id=None,
            lock=lock,
            queueing_lock=queueing_lock,
            task_name=name,
            queue=queue,
            task_kwargs=task_kwargs,
            scheduled_at=schedule_at,
        ),
        job_manager=job_manager,
    )


class Task:
    """
    A task is a function that should be executed later. It is linked to a
    default queue, and expects keyword arguments.

    Attributes
    ----------
    name : ``str``
        Name of the task, usually the dotted path of the decorated function.
    aliases : ``List[str]``
        Additional names for the task.
    retry_strategy : `RetryStrategy`
        Value indicating the retry conditions in case of
        :py:class:`procrastinate.jobs.Job` error.
    pass_context : ``bool``
        If ``True``, passes the task execution context as first positional argument on
        :py:class:`procrastinate.jobs.Job` execution.
    queue : ``str``
        Default queue to send deferred jobs to. The queue can be overridden when a
        job is deferred.
    lock : ``Optional[str]``
        Default lock. The lock can be overridden when a job is deferred.
    queueing_lock : ``Optional[str]``
        Default queueing lock. The queuing lock can be overridden when a job is
        deferred.
    """

    def __init__(
        self,
        func: Callable,
        *,
        blueprint: "blueprints.Blueprint",
        # task naming
        name: Optional[str] = None,
        aliases: Optional[List[str]] = None,
        # task specific settings
        retry: retry_module.RetryValue = False,
        pass_context: bool = False,
        # default defer arguments
        queue: str,
        lock: Optional[str] = None,
        queueing_lock: Optional[str] = None,
    ):
        self.queue = queue
        self.blueprint = blueprint
        self.func: Callable = func
        self.aliases = aliases if aliases else []
        self.retry_strategy = retry_module.get_retry_strategy(retry)
        self.name: str = name if name else self.full_path
        self.pass_context = pass_context
        self.lock = lock
        self.queueing_lock = queueing_lock

    def add_namespace(self, namespace: str) -> None:
        """
        Prefix the given namespace to the name and aliases of the task.
        """
        self.name = utils.add_namespace(name=self.name, namespace=namespace)
        self.aliases = [
            utils.add_namespace(name=alias, namespace=namespace)
            for alias in self.aliases
        ]

    def __call__(self, *args, **kwargs: types.JSONValue) -> Any:
        return self.func(*args, **kwargs)

    @property
    def full_path(self) -> str:
        return utils.get_full_path(self.func)

    async def defer_async(self, **task_kwargs: types.JSONValue) -> int:
        """
        Create a job from this task and the given arguments.
        The job will be created with default parameters, if you want to better
        specify when and how to launch this job, see `Task.configure`.
        """
        return await self.configure().defer_async(**task_kwargs)

    def defer(self, **task_kwargs: types.JSONValue) -> int:
        """
        Create a job from this task and the given arguments.
        The job will be created with default parameters, if you want to better
        specify when and how to launch this job, see `Task.configure`.
        """
        return self.configure().defer(**task_kwargs)

    def configure(
        self,
        *,
        lock: Optional[str] = None,
        queueing_lock: Optional[str] = None,
        task_kwargs: Optional[types.JSONDict] = None,
        schedule_at: Optional[datetime.datetime] = None,
        schedule_in: Optional[Dict[str, int]] = None,
        queue: Optional[str] = None,
    ) -> jobs.JobDeferrer:
        """
        Configure the job with all the specific settings, defining how the job
        should be launched.

        You should call the `defer` method (see `Task.defer`) on the resulting
        object, with the job task parameters.

        Parameters
        ----------
        lock :
            No two jobs with the same lock string can run simultaneously
        queueing_lock :
            No two jobs with the same queueing lock can be waiting in the queue.
            `Task.defer` will raise an `AlreadyEnqueued` exception if there already
            is a job waiting in the queue with same queueing lock.
        task_kwargs :
            Arguments for the job task. You can also pass them to `Task.defer`.
            If you pass both, they will be updated (`Task.defer` has priority)
        schedule_at :
            A datetime before which the job should not be launched (incompatible with
            schedule_in)
        schedule_in :
            A dict with kwargs for a python timedelta, for example ``{'minutes': 5}``.
            Converted to schedule_at internally. See `python timedelta documentation
            <https://docs.python.org/3/library/datetime.html#timedelta-objects>`__
            (incompatible with schedule_at)

        queue :
            By setting a queue on the job launch, you override the task default queue

        Returns
        -------
        ``jobs.JobDeferrer``
            An object with a ``defer`` method, identical to `Task.defer`

        Raises
        ------
        ValueError
            If you try to define both schedule_at and schedule_in
        """
        if not isinstance(self.blueprint, app_module.App):
            raise exceptions.UnboundTaskError

        app = self.blueprint

        return configure_task(
            name=self.name,
            job_manager=app.job_manager,
            lock=lock if lock is not None else self.lock,
            queueing_lock=(
                queueing_lock if queueing_lock is not None else self.queueing_lock
            ),
            task_kwargs=task_kwargs,
            schedule_at=schedule_at,
            schedule_in=schedule_in,
            queue=queue if queue is not None else self.queue,
        )

    def get_retry_exception(
        self, exception: Exception, job: jobs.Job
    ) -> Optional[exceptions.JobRetry]:
        if not self.retry_strategy:
            return None

        return self.retry_strategy.get_retry_exception(
            exception=exception, attempts=job.attempts
        )
