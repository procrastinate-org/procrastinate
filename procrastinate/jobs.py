import datetime
import functools
import logging
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, Optional

import attr

from procrastinate import types, utils

if TYPE_CHECKING:
    from procrastinate import store  # noqa

logger = logging.getLogger(__name__)


DEFAULT_QUEUE = "default"

cached_property = getattr(functools, "cached_property", property)


def check_aware(
    instance: "Job", attribute: attr.Attribute, value: datetime.datetime
) -> None:
    if value and value.utcoffset() is None:
        raise ValueError("Timezone aware datetime is required")


class Status(Enum):
    TODO = "todo"
    DOING = "doing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


@attr.dataclass(frozen=True, kw_only=True)
class Job:
    """
    A job is the launching of a specific task with specific values for the
    keyword arguments.

    Attributes
    ----------
    id :
        Internal id uniquely identifying the job.
    queue :
        Queue name the job will be run in.
    lock :
        Lock object in database that prevents other jobs with the same lock from running
        concurrently.
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
    queue: str
    lock: str
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
            lock=row["lock"],
            task_name=row["task_name"],
            task_kwargs=row["args"],
            scheduled_at=row["scheduled_at"],
            queue=row["queue_name"],
            attempts=row["attempts"],
        )

    def log_context(self) -> types.JSONDict:
        context = attr.asdict(self)

        if context["scheduled_at"]:
            context["scheduled_at"] = context["scheduled_at"].isoformat()

        context["call_string"] = self.call_string
        return context

    @cached_property
    def call_string(self):
        kwargs_string = ", ".join(
            f"{key}={value!r}" for key, value in self.task_kwargs.items()
        )
        return f"{self.task_name}[{self.id}]({kwargs_string})"


@utils.add_sync_api
class JobDeferrer:
    """
    The main purpose of ``JobDeferrer`` is to get a hold of the job_store and the job,
    so that we can call ``defer`` without having to specify the job_store, and the job
    doesn't need a job_store property.
    """

    def __init__(self, job_store: "store.JobStore", job: Job):
        self.job = job
        self.job_store = job_store

    def make_new_job(self, **task_kwargs: types.JSONValue) -> Job:
        final_kwargs = self.job.task_kwargs.copy()
        final_kwargs.update(task_kwargs)

        return attr.evolve(self.job, task_kwargs=final_kwargs)

    async def defer_async(self, **task_kwargs: types.JSONValue) -> int:
        """
        See `Task.defer` for details.
        """

        job = self.make_new_job(**task_kwargs)

        context = job.log_context()
        logger.debug(
            f"About to defer job {job.call_string}",
            extra={"action": "about_to_defer_job", "job": context},
        )
        id = await self.job_store.defer_job(job=job)
        context["id"] = id
        logger.info(
            f"Deferred job {job.call_string} with id: {id}",
            extra={"action": "job_defer", "job": context},
        )
        return id
