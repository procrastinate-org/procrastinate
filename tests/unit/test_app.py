from __future__ import annotations

import asyncio
import collections
from typing import cast

import pytest

from procrastinate import app as app_module
from procrastinate import exceptions, tasks, testing

from .. import conftest


def task_func():
    pass


def test_app_no_connector():
    with pytest.raises(TypeError):
        app_module.App()  # type: ignore


def test_app_task_dont_read_function_attributes(app: app_module.App):
    # This is a weird one. It's a regression test. At some point, we noted that,
    # due to the slightly wrong usage of update_wrapper, the attributes on the
    # decorated function were copied on the task. This led to surprising
    # behaviour. This test is just here to make sure it doesn't happen again.
    def wrapped():
        return "foo"

    wrapped.pass_context = True  # type: ignore
    task = app.task(wrapped)
    assert task.pass_context is False


def test_app_register_builtins(app: app_module.App):
    assert "procrastinate.builtin_tasks.remove_old_jobs" in app.tasks
    assert "builtin:procrastinate.builtin_tasks.remove_old_jobs" in app.tasks


def test_app_register(app: app_module.App):
    task = tasks.Task(task_func, blueprint=app, queue="queue", name="bla")

    app._register_task(task)

    assert "bla" in app.tasks
    assert app.tasks["bla"] == task


def test_app_worker(app: app_module.App, mocker):
    Worker = mocker.patch("procrastinate.worker.Worker")

    app.worker_defaults["timeout"] = 12
    app._worker(queues=["yay"], name="w1", wait=False)

    Worker.assert_called_once_with(
        queues=["yay"], app=app, name="w1", timeout=12, wait=False
    )


def test_app_run_worker(app: app_module.App):
    result = []

    @app.task
    def my_task(a):
        result.append(a)

    my_task.defer(a=1)

    app.run_worker(wait=False)

    assert result == [1]


async def test_app_run_worker_async(app: app_module.App):
    result = []

    @app.task
    async def my_task(a):
        result.append(a)

    await my_task.defer_async(a=1)

    await app.run_worker_async(wait=False)

    assert result == [1]


async def test_app_run_worker_async_cancel(app: app_module.App):
    result = []

    @app.task
    async def my_task(a):
        await asyncio.sleep(0.05)
        result.append(a)

    task = asyncio.create_task(app.run_worker_async())
    await my_task.defer_async(a=1)
    await asyncio.sleep(0.01)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await asyncio.wait_for(task, timeout=0.1)

    assert result == [1]


def test_from_path(mocker):
    load = mocker.patch("procrastinate.utils.load_from_path")
    assert app_module.App.from_path("dotted.path") is load.return_value
    load.assert_called_once_with("dotted.path", app_module.App)


def test_app_configure_task(app: app_module.App):
    scheduled_at = conftest.aware_datetime(2000, 1, 1)
    job = app.configure_task(
        name="my_name",
        queue="marsupilami",
        lock="sher",
        schedule_at=scheduled_at,
        priority=7,
        task_kwargs={"a": 1},
    ).job

    assert job.task_name == "my_name"
    assert job.queue == "marsupilami"
    assert job.lock == "sher"
    assert job.scheduled_at == scheduled_at
    assert job.priority == 7
    assert job.task_kwargs == {"a": 1}


def test_app_configure_task_unknown_allowed(app: app_module.App):
    @app.task(name="my_name", queue="bla")
    def my_name(a):
        pass

    scheduled_at = conftest.aware_datetime(2000, 1, 1)
    job = app.configure_task(
        name="my_name",
        lock="sher",
        schedule_at=scheduled_at,
        priority=7,
        task_kwargs={"a": 1},
    ).job

    assert job.task_name == "my_name"
    assert job.queue == "bla"
    assert job.lock == "sher"
    assert job.scheduled_at == scheduled_at
    assert job.priority == 7
    assert job.task_kwargs == {"a": 1}


def test_app_configure_task_unknown_not_allowed(app: app_module.App):
    with pytest.raises(exceptions.TaskNotFound):
        app.configure_task(name="my_name", allow_unknown=False)


def test_app_periodic(app: app_module.App):
    @app.periodic(cron="0 * * * 1", periodic_id="foo")
    @app.task
    def yay(timestamp: int):
        pass

    assert len(app.periodic_registry.periodic_tasks) == 1
    assert app.periodic_registry.periodic_tasks[yay.name, "foo"].task == yay


@pytest.fixture
def pool(mocker):
    return mocker.MagicMock()


def test_enter_exit(not_opened_app, pool, connector):
    with not_opened_app.open(pool) as app:
        pass

    assert connector.states == ["open", "closed"]
    assert app is not_opened_app  # checks that open returns the app instance


def test_open(not_opened_app, pool, connector):
    app = not_opened_app.open(pool)

    assert connector.states == ["open"]
    assert app is not_opened_app  # checks that open returns the app instance


def test_close(app, connector):
    connector.reset()

    app.close()

    assert connector.states == ["closed"]


async def test_async_enter_exit(not_opened_app, pool, connector):
    async with not_opened_app.open_async(pool) as app:
        pass

    assert connector.states == ["open_async", "closed_async"]
    assert app is not_opened_app  # checks that open_async returns the app instance


async def test_open_async(not_opened_app, pool, connector):
    app = await not_opened_app.open_async(pool)

    assert connector.states == ["open_async"]
    assert app is not_opened_app  # checks that open_async returns the app instance


async def test_close_async(app, connector):
    connector.reset()
    await app.close_async()

    assert connector.states == ["closed_async"]


def test_check_stack(app, caplog):
    caplog.set_level("WARNING")

    app._check_stack()

    assert caplog.records == []


def test_check_stack_main(app, mocker, caplog):
    caplog.set_level("WARNING")
    mocker.patch("procrastinate.utils.caller_module_name", return_value="__main__")

    app._check_stack()

    records = collections.Counter(r.action for r in caplog.records)
    assert records == {"app_defined_in___main__": 1}


def test_check_stack_error(app, mocker, caplog):
    caplog.set_level("WARNING")
    mocker.patch(
        "procrastinate.utils.caller_module_name",
        side_effect=exceptions.CallerModuleUnknown,
    )

    app._check_stack()

    records = collections.Counter(r.action for r in caplog.records)
    assert records == {"app_location_unknown": 1}


def test_check_stack_is_called(mocker, connector):
    # It's a bit ugly but we want one test to fail if __init__ doesn't
    # call _check_stack
    called = []

    class MyApp(app_module.App):
        def _check_stack(self):  # pyright: ignore reportIncompatibleMethodOverride
            called.append(True)
            return "foo"

    MyApp(connector=connector)

    assert called == [True]


def test_with_connector(app, connector):
    new_connector = testing.InMemoryConnector()
    new_app = app.with_connector(connector=new_connector)
    assert new_app is not app

    @app.task(name="foo")
    def foo():
        pass

    @new_app.task(name="bar")
    def bar():
        pass

    assert app.tasks == new_app.tasks
    assert {"foo", "bar"} <= set(app.tasks)

    assert app.connector == connector
    assert new_app.connector == new_connector

    assert app.worker_defaults == new_app.worker_defaults
    assert app.import_paths == new_app.import_paths
    assert app.periodic_registry is new_app.periodic_registry


def test_replace_connector(app: app_module.App):
    @app.task(name="foo")
    def foo():
        pass

    foo.defer()
    assert len(cast(testing.InMemoryConnector, app.connector).jobs) == 1

    new_connector = testing.InMemoryConnector()
    with app.replace_connector(new_connector):
        assert len(cast(testing.InMemoryConnector, app.connector).jobs) == 0

    assert len(cast(testing.InMemoryConnector, app.connector).jobs) == 1
