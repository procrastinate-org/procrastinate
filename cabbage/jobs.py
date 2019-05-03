import logging
from enum import Enum
from typing import Optional

import attr

import cabbage
from cabbage import types

logger = logging.getLogger(__name__)


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
    job_store: "cabbage.store.JobStore"

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
        return attr.asdict(
            self, filter=attr.filters.exclude(attr.fields(Job).job_store)
        )
