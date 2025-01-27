from __future__ import annotations

from collections.abc import Awaitable
from typing import Callable

from procrastinate import job_context

BeforeFetchingJobHook = Callable[[], Awaitable[None]]
JobProcessingStartedHook = Callable[[job_context.JobContext], Awaitable[None]]
JobProcessingEndedHook = Callable[
    [job_context.JobContext, job_context.JobResult], Awaitable[None]
]
