from __future__ import annotations

import pytest

from procrastinate import blueprints, middleware, testing
from procrastinate.contrib.django import db_cleanup


def test_sync_middleware_closes_before_and_after(mocker):
    events = []
    mocker.patch.object(
        db_cleanup, "close_old_connections", side_effect=lambda: events.append("close")
    )
    # reset_queries clears the (DEBUG-only) query log and runs only after the task.
    mocker.patch.object(
        db_cleanup, "reset_queries", side_effect=lambda: events.append("reset")
    )

    def call_next():
        events.append("run")
        return "result"

    result = db_cleanup.close_db_connections(call_next, context=None, worker=None)

    assert result == "result"
    assert events == ["close", "run", "close", "reset"]


def test_sync_middleware_cleans_up_even_on_error(mocker):
    close = mocker.patch.object(db_cleanup, "close_old_connections")
    reset = mocker.patch.object(db_cleanup, "reset_queries")

    def call_next():
        raise ValueError("boom")

    with pytest.raises(ValueError, match="boom"):
        db_cleanup.close_db_connections(call_next, context=None, worker=None)

    # before + after close, and the after-task reset, all still happen.
    assert close.call_count == 2
    assert reset.call_count == 1


async def test_async_middleware_closes_before_and_after(mocker):
    events = []
    # Patch the underlying sync functions. The async middleware routes them through
    # asgiref.sync_to_async, so a thread runs them — appends still happen in order
    # relative to the awaited call_next.
    mocker.patch.object(
        db_cleanup, "close_old_connections", side_effect=lambda: events.append("close")
    )
    mocker.patch.object(
        db_cleanup, "reset_queries", side_effect=lambda: events.append("reset")
    )

    async def call_next():
        events.append("run")
        return "result"

    result = await db_cleanup.close_db_connections_async(
        call_next, context=None, worker=None
    )

    assert result == "result"
    assert events == ["close", "run", "close", "reset"]


async def test_async_middleware_cleans_up_even_on_error(mocker):
    close = mocker.patch.object(db_cleanup, "close_old_connections")
    reset = mocker.patch.object(db_cleanup, "reset_queries")

    async def call_next():
        raise ValueError("boom")

    with pytest.raises(ValueError, match="boom"):
        await db_cleanup.close_db_connections_async(
            call_next, context=None, worker=None
        )

    # before + after close, and the after-task reset, all still happen.
    assert close.call_count == 2
    assert reset.call_count == 1


def test_middleware_kinds_are_detected_correctly():
    # The worker filters worker-wide middleware by kind per task: the sync one must
    # be seen as sync (wraps sync tasks), the async one as async (wraps async tasks).
    assert middleware.is_async_middleware(db_cleanup.close_db_connections) is False
    assert middleware.is_async_middleware(db_cleanup.close_db_connections_async) is True


def test_with_db_cleanup_prepends_both_middlewares():
    result = db_cleanup.with_db_cleanup(None)
    assert result["task_middleware"] == [
        db_cleanup.close_db_connections,
        db_cleanup.close_db_connections_async,
    ]


def test_with_db_cleanup_preserves_user_task_middleware():
    def user_mw(call_next, context, worker):
        return call_next()

    original = {"task_middleware": [user_mw], "concurrency": 5}
    result = db_cleanup.with_db_cleanup(original)

    # User middleware is kept, after ours (ours outermost); other keys untouched.
    assert result["task_middleware"] == [
        db_cleanup.close_db_connections,
        db_cleanup.close_db_connections_async,
        user_mw,
    ]
    assert result["concurrency"] == 5
    # The input dict is not mutated.
    assert original["task_middleware"] == [user_mw]


def test_create_app_wires_db_cleanup_into_worker_defaults():
    from procrastinate.contrib.django import apps

    app = apps.create_app(blueprint=blueprints.Blueprint())

    assert isinstance(app, db_cleanup.DjangoApp)
    task_middleware = app.worker_defaults["task_middleware"]
    assert db_cleanup.close_db_connections in task_middleware
    assert db_cleanup.close_db_connections_async in task_middleware


def test_django_app_merges_db_cleanup_into_worker_defaults():
    app = db_cleanup.DjangoApp(connector=testing.InMemoryConnector())

    assert app.worker_defaults["task_middleware"] == [
        db_cleanup.close_db_connections,
        db_cleanup.close_db_connections_async,
    ]


def test_django_app_preserves_user_worker_defaults():
    def user_mw(call_next, context, worker):
        return call_next()

    app = db_cleanup.DjangoApp(
        connector=testing.InMemoryConnector(),
        worker_defaults={"task_middleware": [user_mw], "concurrency": 5},
    )

    # User middleware kept (after ours, which stay outermost); other keys untouched.
    assert app.worker_defaults["task_middleware"] == [
        db_cleanup.close_db_connections,
        db_cleanup.close_db_connections_async,
        user_mw,
    ]
    assert app.worker_defaults["concurrency"] == 5


def test_django_app_is_publicly_exported():
    # Users build a throwaway DjangoApp in tests (see howto/django/tests); it must
    # be importable from the package.
    from procrastinate.contrib.django import DjangoApp

    assert DjangoApp is db_cleanup.DjangoApp
