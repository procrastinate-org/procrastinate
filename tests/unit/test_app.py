import asyncio
import collections

import pytest

from procrastinate import app as app_module
from procrastinate import exceptions, tasks, testing

from .. import conftest


def task_func():
    pass


def test_app_no_connector():
    with pytest.raises(TypeError):
        app_module.App()


def test_app_task_dont_read_function_attributes(app):
    # This is a weird one. It's a regression test. At some point, we noted that,
    # due to the slightly wrong usage of update_wrapper, the attributes on the
    # decorated function were copied on the task. This led to surprising
    # behaviour. This test is just here to make sure it doesn't happen again.
    def wrapped():
        return "foo"

    wrapped.pass_context = True
    task = app.task(wrapped)
    assert task.pass_context is False


def test_app_register_builtins(app):
    assert "procrastinate.builtin_tasks.remove_old_jobs" in app.tasks
    assert "builtin:procrastinate.builtin_tasks.remove_old_jobs" in app.tasks


def test_app_register(app):
    task = tasks.Task(task_func, blueprint=app, queue="queue", name="bla")

    app._register_task(task)

    assert "bla" in app.tasks
    assert app.tasks["bla"] == task


def test_app_worker(app, mocker):
    Worker = mocker.patch("procrastinate.worker.Worker")

    app.worker_defaults["timeout"] = 12
    app._worker(queues=["yay"], name="w1", wait=False)

    Worker.assert_called_once_with(
        queues=["yay"], app=app, name="w1", timeout=12, wait=False
    )


def test_app_run_worker(app, mocker):
    run = mocker.patch("procrastinate.worker.Worker.run", return_value=asyncio.Future())
    run.return_value.set_result(None)
    app.run_worker(queues=["yay"])

    run.assert_called_once_with()


def test_from_path(mocker):
    load = mocker.patch("procrastinate.utils.load_from_path")
    assert app_module.App.from_path("dotted.path") is load.return_value
    load.assert_called_once_with("dotted.path", app_module.App)


def test_app_configure_task(app):
    scheduled_at = conftest.aware_datetime(2000, 1, 1)
    job = app.configure_task(
        name="my_name",
        queue="marsupilami",
        lock="sher",
        schedule_at=scheduled_at,
        task_kwargs={"a": 1},
    ).job

    assert job.task_name == "my_name"
    assert job.queue == "marsupilami"
    assert job.lock == "sher"
    assert job.scheduled_at == scheduled_at
    assert job.task_kwargs == {"a": 1}


def test_app_configure_task_unknown_allowed(app):
    @app.task(name="my_name", queue="bla")
    def my_name(a):
        pass

    scheduled_at = conftest.aware_datetime(2000, 1, 1)
    job = app.configure_task(
        name="my_name", lock="sher", schedule_at=scheduled_at, task_kwargs={"a": 1}
    ).job

    assert job.task_name == "my_name"
    assert job.queue == "bla"
    assert job.lock == "sher"
    assert job.scheduled_at == scheduled_at
    assert job.task_kwargs == {"a": 1}


def test_app_configure_task_unkown_not_allowed(app):
    with pytest.raises(exceptions.TaskNotFound):
        app.configure_task(name="my_name", allow_unknown=False)


def test_app_periodic(app):
    @app.periodic(cron="0 * * * 1", periodic_id="foo")
    @app.task
    def yay(timestamp):
        pass

    assert len(app.periodic_deferrer.periodic_tasks) == 1
    assert app.periodic_deferrer.periodic_tasks[yay.name, "foo"].task == yay


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
        def _check_stack(self):
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
    assert app.periodic_deferrer is new_app.periodic_deferrer
