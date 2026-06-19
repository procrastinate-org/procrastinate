from __future__ import annotations

import functools
import inspect
from collections.abc import Awaitable, Callable, Sequence
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from procrastinate import job_context, worker

# A sync task middleware wraps a sync task (and runs in the task's worker thread);
# an async task middleware wraps an async task (and runs on the event loop). A
# worker middleware (below) is always async and wraps the whole job on the loop —
# both sync and async tasks. The ``compose`` and ``is_async_middleware`` helpers
# are generic and shared by both.
SyncCallNext = Callable[[], Any]
AsyncCallNext = Callable[[], Awaitable[Any]]
SyncTaskMiddleware = Callable[
    [SyncCallNext, "job_context.JobContext", "worker.Worker"], Any
]
AsyncTaskMiddleware = Callable[
    [AsyncCallNext, "job_context.JobContext", "worker.Worker"], Awaitable[Any]
]
#: A task middleware wraps the execution of a single task. It is a callable
#: taking ``(call_next, context, worker)`` — where ``call_next`` runs the next
#: middleware or the task itself, ``context`` is the
#: :class:`~procrastinate.JobContext` and ``worker`` is the running worker — and
#: must call (or await) ``call_next()`` and return the result. Sync middlewares
#: (plain ``def``) wrap sync tasks; async middlewares (``async def``) wrap async
#: tasks. See :doc:`/howto/advanced/middleware`.
TaskMiddleware = SyncTaskMiddleware | AsyncTaskMiddleware
#: A worker middleware wraps the execution of every job a worker runs, on the
#: event loop. It is a callable taking ``(call_next, context, worker)`` and must
#: be ``async def``. Unlike a task middleware it is always async and wraps both
#: sync and async tasks. See :doc:`/howto/advanced/middleware`.
WorkerMiddleware = Callable[
    [AsyncCallNext, "job_context.JobContext", "worker.Worker"], Awaitable[Any]
]


def is_async_middleware(middleware: TaskMiddleware) -> bool:
    """
    Whether a middleware is a coroutine function (and thus wraps async tasks).
    Handles plain functions, ``functools.partial`` and callable objects.
    """
    func = middleware
    while isinstance(func, functools.partial):
        func = func.func
    if inspect.iscoroutinefunction(func):
        return True
    call = getattr(func, "__call__", None)
    return bool(call is not None and inspect.iscoroutinefunction(call))


def compose(
    middlewares: Sequence[Callable[..., Any]],
    run_task: Callable[[], Any],
    context: job_context.JobContext | None,
    worker: worker.Worker | None,
) -> Callable[[], Any]:
    """
    Nest ``middlewares`` around ``run_task``, first item outermost. Returns a
    zero-arg callable: call it for sync tasks, await its result for async tasks.
    An empty sequence returns ``run_task`` unchanged (no-op).
    """
    call_next = run_task
    for mw in reversed(list(middlewares)):
        call_next = functools.partial(mw, call_next, context, worker)
    return call_next
