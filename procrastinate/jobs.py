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
    DONE = "done"
    ERROR = "error"


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
    job_store: "procrastinate.store.BaseJobStore"

    def defer(self, **task_kwargs: types.JSONValue) -> int:

        final_kwargs = self.task_kwargs.copy()
        final_kwargs.update(task_kwargs)

        job = attr.evolve(self, task_kwargs=final_kwargs)

        id = self.job_store.launch_job(job=job)
        logger.info(
            "Scheduled job", extra={"action": "job_defer", "job": self.get_context()}
        )
        return id

    def get_context(self) -> types.JSONDict:
        context = attr.asdict(
            self, filter=attr.filters.exclude(attr.fields(Job).job_store)
        )

        if context["scheduled_at"]:
            context["scheduled_at"] = context["scheduled_at"].isoformat()

        return context
