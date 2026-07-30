from __future__ import annotations

from typing import TYPE_CHECKING, Any

from asgiref import sync as asgiref_sync
from django.db import close_old_connections, reset_queries

from procrastinate import app as app_module

if TYPE_CHECKING:
    from procrastinate import job_context, worker
    from procrastinate.app import WorkerOptions
    from procrastinate.middleware import AsyncCallNext, SyncCallNext


def _cleanup_before() -> None:
    # Drop a persistent connection (CONN_MAX_AGE > 0) that may have died while the
    # worker pool thread was idle between tasks, so the task transparently
    # reconnects instead of failing on a dead socket. CONN_MAX_AGE is respected:
    # a healthy persistent connection is kept.
    close_old_connections()


def _cleanup_after() -> None:
    # Don't leak the connection past the unit of work...
    close_old_connections()
    # ...and clear Django's per-connection query log. It is only populated when
    # settings.DEBUG is True (and closing the connection does not clear it, since
    # the log lives on the persistent connection wrapper), so without this a
    # worker run with DEBUG=True slowly accumulates it. A no-op when DEBUG is False.
    reset_queries()


def close_db_connections(
    call_next: SyncCallNext,
    context: job_context.JobContext,
    worker: worker.Worker,
) -> Any:
    """
    Sync task middleware that manages Django's per-thread DB connections around a
    sync task, the same way Django manages them around an HTTP request.

    Runs in the worker's asgiref ``sync_to_async`` pool thread — the same thread
    Django opened its per-thread connection in — so closing here targets the right
    connection. Without it, the connection opened by a sync ORM call leaks for the
    lifetime of the (reused) pool thread.

    Note: for the rare sync function that returns an awaitable without being a
    coroutine function (awaited later by the worker), the after-cleanup runs after
    the sync portion returns the awaitable, not after it is awaited. That edge case
    is out of scope here.
    """
    _cleanup_before()
    try:
        return call_next()
    finally:
        _cleanup_after()


# close_old_connections() is @async_unsafe, so the async middleware must not call
# it on the event loop. Route it through sync_to_async(thread_sensitive=True) so it
# runs in Django's thread-sensitive context (the same context the async ORM used).
_cleanup_before_async = asgiref_sync.sync_to_async(
    _cleanup_before, thread_sensitive=True
)
_cleanup_after_async = asgiref_sync.sync_to_async(_cleanup_after, thread_sensitive=True)


async def close_db_connections_async(
    call_next: AsyncCallNext,
    context: job_context.JobContext,
    worker: worker.Worker,
) -> Any:
    """
    Async task middleware that manages Django's per-thread DB connections around an
    async task. Mirrors :func:`close_db_connections` but runs the cleanup via
    ``sync_to_async`` because the async task runs on the event loop and
    ``close_old_connections`` is ``@async_unsafe``.
    """
    await _cleanup_before_async()
    try:
        return await call_next()
    finally:
        await _cleanup_after_async()


def with_db_cleanup(worker_defaults: WorkerOptions | None) -> WorkerOptions:
    """
    Return a copy of ``worker_defaults`` with the Django DB-cleanup middlewares
    prepended to ``task_middleware``. Ours go first so they sit *outermost*, around
    any user-supplied worker-wide middleware. The worker kind-filters them per task,
    so each task gets exactly the matching one.
    """
    base: WorkerOptions = worker_defaults or {}
    existing = list(base.get("task_middleware") or [])
    result: WorkerOptions = {
        **base,
        "task_middleware": [
            close_db_connections,
            close_db_connections_async,
            *existing,
        ],
    }
    return result


class DjangoApp(app_module.App):
    """
    A :class:`procrastinate.App` preconfigured to manage Django's per-thread
    database connections around each task (see :func:`close_db_connections`).

    This is the app the Django contrib runs (``procrastinate.contrib.django.app``).
    It is also the app to use when building a throwaway app in a test — e.g. to
    avoid leaving a task registered on the global app — so that tasks run by a
    worker get the same connection cleanup and don't leak connections at test
    database teardown::

        from procrastinate.contrib.django import DjangoApp, app

        new_app = DjangoApp(connector=app.connector)

    The cleanup is configured by merging the DB-cleanup middlewares into
    ``worker_defaults`` (see :func:`with_db_cleanup`); any ``worker_defaults`` you
    pass are preserved.
    """

    def __init__(
        self, *, worker_defaults: WorkerOptions | None = None, **kwargs: Any
    ) -> None:
        super().__init__(worker_defaults=with_db_cleanup(worker_defaults), **kwargs)
