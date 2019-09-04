import datetime
import logging
from enum import Enum
from typing import Optional

import attr

import procrastinate
from procrastinate import types

logger = logging.getLogger(__name__)


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

    def defer(
        self, job_store: "procrastinate.store.BaseJobStore", task_kwargs: types.JSONDict
    ) -> int:
        final_kwargs = self.task_kwargs.copy()
        final_kwargs.update(task_kwargs)

        job = attr.evolve(self, task_kwargs=final_kwargs)

        id = job_store.launch_job(job=job)
        logger.info(
            "Scheduled job", extra={"action": "job_defer", "job": self.get_context()}
        )
        return id

    def get_context(self) -> types.JSONDict:
        context = attr.asdict(self)

        if context["scheduled_at"]:
            context["scheduled_at"] = context["scheduled_at"].isoformat()

        return context


class JobLauncher:
    """
    The main purpose of JobLauncher is to get a hold of the job_store and the job, so
    that we can call ``defer`` without having to specify the job_store, and the job
    doesn't need a job_store property.
    """

    def __init__(self, job_store: "procrastinate.store.BaseJobStore", job: Job):
        self.job = job
        self.job_store = job_store

    def defer(self, **task_kwargs: types.JSONValue) -> int:
        """
        See :py:func:`Task.defer` for details.
        """
        return self.job.defer(job_store=self.job_store, task_kwargs=task_kwargs)
