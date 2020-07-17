import datetime
import logging
from typing import Any, Callable, Dict, List, Optional

from procrastinate import app, exceptions, jobs
from procrastinate import retry as retry_module
from procrastinate import store, types, utils

logger = logging.getLogger(__name__)


def load_task(path: str) -> "Task":
    try:
        task = utils.load_from_path(path, Task)
    except exceptions.LoadFromPathError as exc:
        raise exceptions.TaskNotFound(f"Task at {path} cannot be imported: {str(exc)}")

    return task


def configure_task(
    *,
    name: str,
    job_store: store.JobStore,
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
        job_store=job_store,
    )


class Task:
    """
    A task is a function that should be executed later. It is linked to a
    default queue, and expects keyword arguments.

    Attributes
    ----------
    queue : ``str``
        Default queue to send deferred jobs to.
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
    """

    def __init__(
        self,
        func: Callable,
        *,
        app: app.App,
        queue: str,
        name: Optional[str] = None,
        aliases: Optional[List[str]] = None,
        retry: retry_module.RetryValue = False,
        pass_context: bool = False,
    ):
        self.queue = queue
        self.app = app
        self.func: Callable = func
        self.aliases = aliases if aliases else []
        self.retry_strategy = retry_module.get_retry_strategy(retry)
        self.name: str = name if name else self.full_path
        self.pass_context = pass_context

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
            A dict describing the time interval before the task should be launched.
            See details in the `python documentation
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
        return configure_task(
            name=self.name,
            job_store=self.app.job_store,
            lock=lock,
            queueing_lock=queueing_lock,
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
