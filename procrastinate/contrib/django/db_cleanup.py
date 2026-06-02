from __future__ import annotations

import functools
import inspect
from typing import TYPE_CHECKING, Any

from asgiref import sync as asgiref_sync
from django.db import close_old_connections

from procrastinate import app as app_module
from procrastinate import blueprints

if TYPE_CHECKING:
    from procrastinate import tasks

# Sentinel attribute set on a wrapped task function so wrapping is idempotent
# (a task may be registered under several names/aliases or merged more than once).
_WRAPPED_FLAG = "_procrastinate_django_db_cleanup"


def wrap_task(task: tasks.Task) -> None:
    """
    Wrap a task's function so that Django's per-thread database connections are
    closed before and after the task runs.

    Procrastinate sync tasks run inside an asgiref ``sync_to_async`` worker-pool
    thread (see ``procrastinate.worker``). Django's connection cache is
    thread-local and the caller owns closing connections in non-request contexts,
    so without this the connection opened by a sync ORM call leaks for the
    lifetime of the (reused) pool thread. We mirror Django's own request lifecycle
    (``close_old_connections`` wired to both ``request_started`` and
    ``request_finished``) by closing around each task:

    - before: drop a persistent connection (``CONN_MAX_AGE > 0``) that may have
      died while the pool thread was idle between tasks, so the task transparently
      reconnects instead of failing on a dead socket;
    - after: don't leak the connection past the unit of work.

    ``close_old_connections`` respects ``CONN_MAX_AGE``: a healthy persistent
    connection is kept, while with the default ``CONN_MAX_AGE = 0`` every
    connection is closed.

    The wrapper preserves the sync/async nature of the original function so the
    worker's ``inspect.iscoroutinefunction`` detection keeps working.
    """
    func = task.func
    if getattr(func, _WRAPPED_FLAG, False):
        return

    if inspect.iscoroutinefunction(func):

        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            # The task runs in the event-loop thread. Django's connection.close()
            # is @async_unsafe, so we close in Django's thread-sensitive context
            # (where the async ORM ran its sync work) via sync_to_async.
            aclose = asgiref_sync.sync_to_async(
                close_old_connections, thread_sensitive=True
            )
            await aclose()
            try:
                return await func(*args, **kwargs)
            finally:
                await aclose()

        wrapper = async_wrapper

    else:

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            # Runs in the worker's sync_to_async pool thread, the same thread
            # Django opened its per-thread connection in.
            # Note: for the rare sync function that returns an awaitable without
            # being a coroutine function (awaited later by the worker), the final
            # close happens after the sync portion returns the awaitable, not
            # after it is awaited. That edge case is out of scope here.
            close_old_connections()
            try:
                return func(*args, **kwargs)
            finally:
                close_old_connections()

        wrapper = sync_wrapper

    setattr(wrapper, _WRAPPED_FLAG, True)
    task.func = wrapper


class DjangoApp(app_module.App):
    """
    A :class:`procrastinate.App` that automatically closes Django's per-thread
    database connections around each task execution (see :func:`wrap_task`).

    Every task reaches the registry through ``_register_task`` (the ``@app.task``
    decorator) or ``add_tasks_from`` (builtin tasks, the contrib ``FutureApp``
    blueprint, and any ``on_app_ready`` blueprints), so wrapping in both covers
    all registration paths.
    """

    def _register_task(self, task: tasks.Task) -> None:
        super()._register_task(task)
        wrap_task(task)

    def add_tasks_from(
        self, blueprint: blueprints.Blueprint, *, namespace: str
    ) -> None:
        super().add_tasks_from(blueprint, namespace=namespace)
        # After the merge, blueprint.tasks holds the (namespaced) task objects.
        for task in blueprint.tasks.values():
            wrap_task(task)
