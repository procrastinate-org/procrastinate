from __future__ import annotations

import datetime
import logging
from typing import Any, Callable, Generic, TypedDict, cast

from typing_extensions import NotRequired, ParamSpec, Unpack

from procrastinate import app as app_module
from procrastinate import blueprints, exceptions, jobs, manager, types, utils
from procrastinate import retry as retry_module

logger = logging.getLogger(__name__)


Args = ParamSpec("Args")
P = ParamSpec("P")


class TimeDeltaParams(TypedDict):
    weeks: NotRequired[int]
    days: NotRequired[int]
    hours: NotRequired[int]
    minutes: NotRequired[int]
    seconds: NotRequired[int]
    milliseconds: NotRequired[int]
    microseconds: NotRequired[int]


class ConfigureTaskOptions(TypedDict):
    lock: NotRequired[str | None]
    queueing_lock: NotRequired[str | None]
    task_kwargs: NotRequired[types.JSONDict | None]
    schedule_at: NotRequired[datetime.datetime | None]
    schedule_in: NotRequired[TimeDeltaParams | None]
    queue: NotRequired[str | None]
    priority: NotRequired[int | None]


def configure_task(
    *,
    name: str,
    job_manager: manager.JobManager,
    **options: Unpack[ConfigureTaskOptions],
) -> jobs.JobDeferrer:
    schedule_at = options.get("schedule_at")
    schedule_in = options.get("schedule_in")
    priority = options.get("priority")

    if schedule_at and schedule_in is not None:
        raise ValueError("Cannot set both schedule_at and schedule_in")

    if schedule_in is not None:
        schedule_at = utils.utcnow() + datetime.timedelta(**schedule_in)

    if priority is None:
        priority = jobs.DEFAULT_PRIORITY

    task_kwargs = options.get("task_kwargs") or {}
    return jobs.JobDeferrer(
        job=jobs.Job(
            id=None,
            lock=options.get("lock"),
            queueing_lock=options.get("queueing_lock"),
            task_name=name,
            queue=options.get("queue") or jobs.DEFAULT_QUEUE,
            task_kwargs=task_kwargs,
            scheduled_at=schedule_at,
            priority=priority,
        ),
        job_manager=job_manager,
    )


class Task(Generic[P, Args]):
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
    priority :
        Default priority (an integer) of jobs that are deferred from this task.
        Jobs with higher priority are run first. Priority can be positive or negative.
        If no default priority is set then the default priority is 0.
    lock : ``Optional[str]``
        Default lock. The lock can be overridden when a job is deferred.
    queueing_lock : ``Optional[str]``
        Default queueing lock. The queuing lock can be overridden when a job is
        deferred.
    """

    def __init__(
        self,
        func: Callable[P],
        *,
        blueprint: blueprints.Blueprint,
        # task naming
        name: str | None = None,
        aliases: list[str] | None = None,
        # task specific settings
        retry: retry_module.RetryValue = False,
        pass_context: bool = False,
        # default defer arguments
        queue: str,
        priority: int = jobs.DEFAULT_PRIORITY,
        lock: str | None = None,
        queueing_lock: str | None = None,
    ):
        self.queue = queue
        self.priority = priority
        self.blueprint = blueprint
        self.func: Callable[P] = func
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

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> Any:
        return self.func(*args, **kwargs)

    @property
    def full_path(self) -> str:
        return utils.get_full_path(self.func)

    async def defer_async(self, *_: Args.args, **task_kwargs: Args.kwargs) -> int:
        """
        Create a job from this task and the given arguments.
        The job will be created with default parameters, if you want to better
        specify when and how to launch this job, see `Task.configure`.
        """
        return await self.configure().defer_async(**task_kwargs)

    def defer(self, *_: Args.args, **task_kwargs: Args.kwargs) -> int:
        """
        Create a job from this task and the given arguments.
        The job will be created with default parameters, if you want to better
        specify when and how to launch this job, see `Task.configure`.
        """
        return self.configure().defer(**task_kwargs)

    def configure(self, **options: Unpack[ConfigureTaskOptions]) -> jobs.JobDeferrer:
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
        priority :
            Set the priority of the job as an integer. Jobs with higher priority
            are run first. Priority can be positive or negative. The default priority
            is 0.

        Returns
        -------
        ``jobs.JobDeferrer``
            An object with a ``defer`` method, identical to `Task.defer`

        Raises
        ------
        ValueError
            If you try to define both schedule_at and schedule_in
        """
        self.blueprint.will_configure_task()

        lock = options.get("lock")
        queueing_lock = options.get("queueing_lock")
        task_kwargs = options.get("task_kwargs")
        schedule_at = options.get("schedule_at")
        schedule_in = options.get("schedule_in")
        queue = options.get("queue")
        priority = options.get("priority")

        app = cast(app_module.App, self.blueprint)
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
            priority=priority if priority is not None else self.priority,
        )

    def get_retry_exception(
        self, exception: BaseException, job: jobs.Job
    ) -> exceptions.JobRetry | None:
        if not self.retry_strategy:
            return None

        return self.retry_strategy.get_retry_exception(
            exception=exception, attempts=job.attempts
        )
