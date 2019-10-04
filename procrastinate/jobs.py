import datetime
import logging
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, Optional, Union

import attr

from procrastinate import types

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

        return context


class JobDeferrer:
    """
    The main purpose of JobDeferrer is to get a hold of the job_store and the job, so
    that we can call ``defer`` without having to specify the job_store, and the job
    doesn't need a job_store property.
    """

    def __init__(
        self,
        job_store: Union["store.BaseJobStore", "store.AsyncBaseJobStore"],
        job: Job,
    ):
        self.job = job
        self.job_store = job_store

    def make_new_job(self, **task_kwargs: types.JSONValue) -> Job:
        final_kwargs = self.job.task_kwargs.copy()
        final_kwargs.update(task_kwargs)

        return attr.evolve(self.job, task_kwargs=final_kwargs)

    def defer(self, **task_kwargs: types.JSONValue) -> int:
        """
        See :py:func:`Task.defer` for details.
        """
        from procrastinate import store as store_module

        assert isinstance(
            self.job_store, store_module.BaseJobStore
        ), "defer() can only be used with a sync job store. Use defer_async()."

        job = self.make_new_job(**task_kwargs)

        logger.info(
            "Deferring job", extra={"action": "job_defer", "job": job.get_context()}
        )
        id = self.job_store.defer_job(job=job)
        return id

    async def defer_async(self, **task_kwargs: types.JSONValue) -> int:
        """
        See :py:func:`Task.defer` for details.
        """
        from procrastinate import store as store_module

        assert isinstance(
            self.job_store, store_module.AsyncBaseJobStore
        ), "defer_async() can only be used with an async job store. Use defer()."

        job = self.make_new_job(**task_kwargs)

        logger.info(
            "Deferring job",
            extra={
                "action": "job_defer",
                "asynchronous": True,
                "job": job.get_context(),
            },
        )
        id = await self.job_store.defer_job(job=job)
        return id
