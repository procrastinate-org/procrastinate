from __future__ import annotations

from collections.abc import Awaitable
from typing import TYPE_CHECKING, Callable

from procrastinate import job_context

if TYPE_CHECKING:
    from procrastinate import worker

ProcessTask = Callable[..., Awaitable]
Middleware = Callable[[ProcessTask, job_context.JobContext, "worker.Worker"], Awaitable]


async def default_middleware(
    process_task: ProcessTask, context: job_context.JobContext, worker: worker.Worker
):
    return await process_task()
