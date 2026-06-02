from __future__ import annotations

import inspect

import pytest

from procrastinate import blueprints, testing
from procrastinate.contrib.django import db_cleanup
from procrastinate.tasks import Task


def make_task(func, name="task"):
    return Task(func=func, blueprint=blueprints.Blueprint(), queue="default", name=name)


def test_wrap_task_sync_closes_before_and_after(mocker):
    events = []
    mocker.patch.object(
        db_cleanup,
        "close_old_connections",
        side_effect=lambda: events.append("close"),
    )
    task = make_task(lambda: events.append("run"))

    db_cleanup.wrap_task(task)
    task.func()

    assert events == ["close", "run", "close"]


def test_wrap_task_sync_closes_even_on_error(mocker):
    close = mocker.patch.object(db_cleanup, "close_old_connections")

    def boom():
        raise ValueError("boom")

    task = make_task(boom)
    db_cleanup.wrap_task(task)

    with pytest.raises(ValueError):
        task.func()

    assert close.call_count == 2


async def test_wrap_task_async_closes_before_and_after(mocker):
    events = []
    mocker.patch.object(
        db_cleanup,
        "close_old_connections",
        side_effect=lambda: events.append("close"),
    )

    async def coro():
        events.append("run")

    task = make_task(coro)
    db_cleanup.wrap_task(task)
    await task.func()

    assert events == ["close", "run", "close"]


def test_wrap_task_preserves_sync_or_async_nature():
    def sync_func():
        pass

    async def async_func():
        pass

    sync_task = make_task(sync_func)
    async_task = make_task(async_func)

    db_cleanup.wrap_task(sync_task)
    db_cleanup.wrap_task(async_task)

    # The worker branches on inspect.iscoroutinefunction(task.func), so wrapping
    # must not change it.
    assert inspect.iscoroutinefunction(sync_task.func) is False
    assert inspect.iscoroutinefunction(async_task.func) is True


def test_wrap_task_is_idempotent():
    task = make_task(lambda: None)

    db_cleanup.wrap_task(task)
    wrapped_once = task.func
    db_cleanup.wrap_task(task)

    assert task.func is wrapped_once


def test_django_app_wraps_tasks_from_both_registration_paths():
    app = db_cleanup.DjangoApp(connector=testing.InMemoryConnector())

    @app.task(name="decorated")
    def decorated():
        pass

    bp = blueprints.Blueprint()

    @bp.task(name="from_blueprint")
    def from_blueprint():
        pass

    app.add_tasks_from(bp, namespace="ns")

    flag = db_cleanup._WRAPPED_FLAG
    assert getattr(app.tasks["decorated"].func, flag, False) is True
    assert getattr(app.tasks["ns:from_blueprint"].func, flag, False) is True
    # Builtin tasks (registered via add_tasks_from in App.__init__) too.
    assert all(getattr(t.func, flag, False) for t in app.tasks.values())
