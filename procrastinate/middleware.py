from __future__ import annotations

from collections.abc import Awaitable
from typing import TYPE_CHECKING, Callable, TypeVar

from procrastinate import job_context

R = TypeVar("R")

if TYPE_CHECKING:
    from procrastinate import worker

ProcessTask = Callable[..., R]
WorkerMiddleware = Callable[
    [ProcessTask[Awaitable], job_context.JobContext, "worker.Worker"], Awaitable
]
TaskMiddleware = Callable[[ProcessTask[R], job_context.JobContext, "worker.Worker"], R]


async def default_worker_middleware(
    process_task: ProcessTask,
    context: job_context.JobContext,
    worker: worker.Worker,
):
    return await process_task()


async def default_async_task_middleware(
    process_task: ProcessTask,
    context: job_context.JobContext,
    worker: worker.Worker,
):
    return await process_task()


def default_sync_task_middleware(
    process_task: ProcessTask,
    context: job_context.JobContext,
    worker: worker.Worker,
):
    return process_task()
