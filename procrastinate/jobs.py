import datetime
import functools
import logging
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, Optional

import attr

from procrastinate import types

if TYPE_CHECKING:
    from procrastinate import manager

logger = logging.getLogger(__name__)


DEFAULT_QUEUE = "default"

cached_property = getattr(functools, "cached_property", property)


def check_aware(
    instance: "Job", attribute: attr.Attribute, value: datetime.datetime
) -> None:
    if value and value.utcoffset() is None:
        raise ValueError("Timezone aware datetime is required")


class Status(Enum):
    """
    An enumeration with all the possible job statuses.
    """

    TODO = "todo"  #: The job is waiting in a queue
    DOING = "doing"  #: A worker is running the job
    SUCCEEDED = "succeeded"  #: The job ended successfully
    FAILED = "failed"  #: The job ended with an error


@attr.dataclass(frozen=True, kw_only=True)
class Job:
    """
    A job is the launching of a specific task with specific values for the
    keyword arguments.

    Attributes
    ----------
    id :
        Internal id uniquely identifying the job.
    status :
        Status of the job.
    queue :
        Queue name the job will be run in.
    lock :
        No two jobs with the same lock string can run simultaneously
    queueing_lock :
        No two jobs with the same queueing lock can be waiting in the queue.
    task_name :
        Name of the associated task.
    task_kwargs :
        Arguments used to call the task.
    scheduled_at :
        Date and time after which the job is expected to run.
    attempts :
        Number of times the job has been tried.
    """

    id: Optional[int] = None
    status: Optional[str] = None
    queue: str
    lock: Optional[str]
    queueing_lock: Optional[str]
    task_name: str
    task_kwargs: types.JSONDict = attr.ib(factory=dict)
    scheduled_at: Optional[datetime.datetime] = attr.ib(
        default=None, validator=check_aware
    )
    attempts: int = 0

    @classmethod
    def from_row(cls, row: Dict[str, Any]) -> "Job":
        return cls(
            id=row["id"],
            status=row["status"],
            lock=row["lock"],
            queueing_lock=row["queueing_lock"],
            task_name=row["task_name"],
            task_kwargs=row["args"],
            scheduled_at=row["scheduled_at"],
            queue=row["queue_name"],
            attempts=row["attempts"],
        )

    def asdict(self) -> Dict[str, Any]:
        return attr.asdict(self)

    def log_context(self) -> types.JSONDict:
        context = self.asdict()

        if context["scheduled_at"]:
            context["scheduled_at"] = context["scheduled_at"].isoformat()

        context["call_string"] = self.call_string
        return context

    def evolve(self, **kwargs: Any) -> "Job":
        return attr.evolve(self, **kwargs)

    @cached_property
    def call_string(self):
        kwargs_string = ", ".join(
            f"{key}={value!r}" for key, value in self.task_kwargs.items()
        )
        return f"{self.task_name}[{self.id}]({kwargs_string})"


class JobDeferrer:
    """
    The main purpose of ``JobDeferrer`` is to get a hold of the job_manager and the job,
    so that we can call ``defer`` without having to specify the job_manager, and the job
    doesn't need a job_manager property.
    """

    def __init__(self, job_manager: "manager.JobManager", job: Job):
        self.job = job
        self.job_manager = job_manager

    def make_new_job(self, **task_kwargs: types.JSONValue) -> Job:
        final_kwargs = self.job.task_kwargs.copy()
        final_kwargs.update(task_kwargs)

        return self.job.evolve(task_kwargs=final_kwargs)

    def _log_before_defer_job(self, job: Job) -> None:
        logger.debug(
            f"About to defer job {job.call_string}",
            extra={"action": "about_to_defer_job", "job": job.log_context()},
        )

    def _log_after_defer_job(self, job: Job) -> None:

        logger.info(
            f"Deferred job {job.call_string}",
            extra={"action": "job_defer", "job": job.log_context()},
        )

    async def defer_async(self, **task_kwargs: types.JSONValue) -> int:
        """
        See `Task.defer` for details.
        """
        # Make sure this code stays synchronized with .defer()
        job = self.make_new_job(**task_kwargs)
        self._log_before_defer_job(job=job)
        job = await self.job_manager.defer_job_async(job=job)
        self._log_after_defer_job(job=job)
        assert job.id  # for mypy
        return job.id

    def defer(self, **task_kwargs: types.JSONValue) -> int:
        # Make sure this code stays synchronized with .defer_async()
        job = self.make_new_job(**task_kwargs)
        self._log_before_defer_job(job=job)
        job = self.job_manager.defer_job(job=job)
        self._log_after_defer_job(job=job)
        assert job.id  # for mypy
        return job.id
