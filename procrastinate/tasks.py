import datetime
import logging
import uuid
from typing import Any, Callable, Dict, Optional

import pendulum

from procrastinate import app, exceptions, jobs
from procrastinate import retry as retry_module
from procrastinate import types, utils

logger = logging.getLogger(__name__)


def load_task(path: str) -> "Task":
    try:
        task = utils.load_from_path(path, Task)
    except exceptions.LoadFromPathError as exc:
        raise exceptions.TaskNotFound(f"Task at {path} cannot be imported: {str(exc)}")

    return task


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
        self.name: str
        if name:
            self.name = name
        else:
            self.name = self.full_path

        if name:
            try:
                full_path = self.full_path
            except AttributeError:
                # Can happen for functools.partial for example
                full_path = ""

            if full_path and name != full_path:
                logger.warning(
                    f"Task {name} at {self.full_path} has a name that doesn't match "
                    "its import path. Please make sure its module path is provided in "
                    "the worker's import_paths, or it won't run.",
                    extra={
                        "action": "task_name_differ_from_path",
                        "task_name": name,
                        "task_path": self.full_path,
                    },
                )

    def __call__(self, **kwargs: types.JSONValue) -> Any:
        return self.func(**kwargs)

    @property
    def full_path(self) -> str:
        return f"{self.func.__module__}.{self.func.__name__}"

    def defer(self, **task_kwargs: types.JSONValue) -> int:
        """
        Create a job from this task and the given arguments.
        The job will be created with default parameters, if you want to better
        specify when and how to launch this job, see :py:func:`Task.configure`
        """
        job_id = self.configure().defer(**task_kwargs)

        return job_id

    def configure(
        self,
        *,
        lock: Optional[str] = None,
        task_kwargs: Optional[types.JSONDict] = None,
        schedule_at: Optional[datetime.datetime] = None,
        schedule_in: Optional[Dict[str, int]] = None,
        queue: Optional[str] = None,
    ) -> jobs.JobLauncher:
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
        jobs.JobLauncher
            An object with a ``defer`` method, identical to :py:func:`Task.defer`

        Raises
        ------
        ValueError
            If you try to define both schedule_at and schedule_in
        """
        if schedule_at and schedule_in is not None:
            raise ValueError("Cannot set both schedule_at and schedule_in")

        if schedule_in is not None:
            schedule_at = pendulum.now("UTC").add(**schedule_in)

        lock = lock or str(uuid.uuid4())
        task_kwargs = task_kwargs or {}
        return jobs.JobLauncher(
            job=jobs.Job(
                id=None,
                lock=lock,
                task_name=self.name,
                queue=queue if queue is not None else self.queue,
                task_kwargs=task_kwargs,
                scheduled_at=schedule_at,
            ),
            job_store=self.app.job_store,
        )

    def get_retry_exception(self, job: jobs.Job) -> Optional[exceptions.JobRetry]:
        if not self.retry_strategy:
            return None

        return self.retry_strategy.get_retry_exception(job.attempts)
