import datetime
import logging
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, Optional

import attr

from procrastinate import types, utils

if TYPE_CHECKING:
    from procrastinate import store  # noqa

logger = logging.getLogger(__name__)


DEFAULT_QUEUE = "default"


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

    def get_context(self) -> types.JSONDict:
        context = attr.asdict(self)

        if context["scheduled_at"]:
            context["scheduled_at"] = context["scheduled_at"].isoformat()
        kwargs_string = ", ".join(
            f"{key}={value}" for key, value in context["task_kwargs"].items()
        )
        context["call_string"] = f"{context['task_name']}({kwargs_string})"
        return context


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
        See :py:func:`Task.defer` for details.
        """

        job = self.make_new_job(**task_kwargs)

        context = job.get_context()
        logger.debug(
            f"About to defer job {context['call_string']}",
            extra={"action": "about_to_job_defer", "job": context},
        )
        id = await self.job_store.defer_job(job=job)
        context["id"] = id
        logger.info(
            f"Deferred job {context['call_string']} with id: {id}",
            extra={"action": "job_defer", "job": context},
        )
        return id
