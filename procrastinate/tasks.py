import datetime
import logging
import uuid
from typing import Any, Callable, Dict, Optional

import pendulum

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
    task_kwargs: Optional[types.JSONDict] = None,
    schedule_at: Optional[datetime.datetime] = None,
    schedule_in: Optional[Dict[str, int]] = None,
    queue: str = jobs.DEFAULT_QUEUE,
) -> jobs.JobDeferrer:
    if schedule_at and schedule_in is not None:
        raise ValueError("Cannot set both schedule_at and schedule_in")

    if schedule_in is not None:
        schedule_at = pendulum.now("UTC").add(**schedule_in)

    lock = lock or str(uuid.uuid4())
    task_kwargs = task_kwargs or {}
    return jobs.JobDeferrer(
        job=jobs.Job(
            id=None,
            lock=lock,
            task_name=name,
            queue=queue,
            task_kwargs=task_kwargs,
            scheduled_at=schedule_at,
        ),
        job_store=job_store,
    )


@utils.add_sync_api
class Task:
    def __init__(
        self,
        func: Callable,
        *,
        app: app.App,
        queue: str,
        name: Optional[str] = None,
        retry: retry_module.RetryValue = False,
    ):
        self.queue = queue
        self.app = app
        self.func: Callable = func
        self.retry_strategy = retry_module.get_retry_strategy(retry)
        self.name: str = name if name else self.full_path

    def __call__(self, **kwargs: types.JSONValue) -> Any:
        return self.func(**kwargs)

    @property
    def full_path(self) -> str:
        return f"{self.func.__module__}.{self.func.__name__}"

    async def defer_async(self, **task_kwargs: types.JSONValue) -> int:
        """
        Create a job from this task and the given arguments.
        The job will be created with default parameters, if you want to better
        specify when and how to launch this job, see :py:func:`Task.configure`.
        """
        job_id = await self.configure().defer_async(**task_kwargs)

        return job_id

    def configure(
        self,
        *,
        lock: Optional[str] = None,
        task_kwargs: Optional[types.JSONDict] = None,
        schedule_at: Optional[datetime.datetime] = None,
        schedule_in: Optional[Dict[str, int]] = None,
        queue: Optional[str] = None,
    ) -> jobs.JobDeferrer:
        """
        Configure the job with all the specific settings, defining how the job
        should be launched.

        You should call the `defer` method (see :py:func:`Task.defer`) on the resulting
        object, with the job task parameters.

        Parameters
        ----------
        lock :
            No two jobs with the same lock string can run simultaneously
        task_kwargs :
            Arguments for the job task. You can also pass them to :py:func:`Task.defer`.
            If you pass both, they will be updated (:py:func:`Task.defer` has priority)
        schedule_at :
            A datetime before which the job should not be launched (incompatible with
            schedule_in)
        schedule_in :
            A dict describing the time interval before the task should be launched.
            See details in the `pendulum documentation
            <https://pendulum.eustace.io/docs/#addition-and-subtraction>`__
            (incompatible with schedule_at)

        queue :
            By setting a queue on the job launch, you override the task default queue

        Returns
        -------
        ``jobs.JobDeferrer``
            An object with a ``defer`` method, identical to :py:func:`Task.defer`

        Raises
        ------
        ValueError
            If you try to define both schedule_at and schedule_in
        """
        return configure_task(
            name=self.name,
            job_store=self.app.job_store,
            lock=lock,
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
