import asyncio

import pytest

from procrastinate import app as app_module
from procrastinate import tasks

from .. import conftest
from .conftest import AsyncMock


def task_func():
    pass


def test_app_no_connector():
    with pytest.raises(TypeError):
        app_module.App()


def test_app_task_explicit(app, mocker):
    @app.task(queue="a", name="b")
    def wrapped():
        return "foo"

    assert "foo" == wrapped()
    assert "b" == app.tasks["b"].name
    assert "a" == app.tasks["b"].queue
    assert app.tasks["b"] is wrapped
    assert app.tasks["b"].func is wrapped.__wrapped__


def test_app_task_aliases(app, mocker):
    @app.task(name="b", aliases=["c", "d"])
    def wrapped():
        pass

    assert "b" == app.tasks["b"].name
    assert ["c", "d"] == app.tasks["b"].aliases
    assert app.tasks["b"] is wrapped
    assert app.tasks["c"] is wrapped
    assert app.tasks["d"] is wrapped


def test_app_task_implicit(app, mocker):
    @app.task
    def wrapped():
        return "foo"

    registered_task = app.tasks["tests.unit.test_app.wrapped"]

    assert "foo" == wrapped()
    assert "tests.unit.test_app.wrapped" == registered_task.name
    assert "default" == registered_task.queue
    assert registered_task is wrapped
    assert registered_task.func is wrapped.__wrapped__


def test_app_register_builtins(app):
    assert app.queues == {"builtin"}
    assert "procrastinate.builtin_tasks.remove_old_jobs" in app.tasks
    assert "remove_old_jobs" in app.builtin_tasks


def test_app_register(app):
    task = tasks.Task(task_func, app=app, queue="queue", name="bla")

    app._register(task)

    assert app.queues == {"queue", "builtin"}
    assert "bla" in app.tasks
    assert app.tasks["bla"] == task


def test_app_register_queue_already_exists(app):
    app.queues.add("queue")
    task = tasks.Task(task_func, app=app, queue="queue", name="bla")

    app._register(task)

    assert app.queues == {"queue", "builtin"}
    assert "bla" in app.tasks
    assert app.tasks["bla"] == task


def test_app_worker(app, mocker):
    Worker = mocker.patch("procrastinate.worker.Worker")

    app.worker_defaults["timeout"] = 12
    app._worker(queues=["yay"], name="w1", wait=False)

    Worker.assert_called_once_with(
        queues=["yay"], app=app, name="w1", timeout=12, wait=False,
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


def test_app_periodic(app):
    @app.periodic(cron="0 * * * 1")
    @app.task
    def yay(timestamp):
        pass

    assert len(app.periodic_deferrer.periodic_tasks) == 1
    assert app.periodic_deferrer.periodic_tasks[0].task == yay


@pytest.fixture
def mock_connector_open(app, mocker):
    return mocker.patch.object(app.connector, "open")


@pytest.fixture
def mock_connector_close(app, mocker):
    return mocker.patch.object(app.connector, "close")


@pytest.fixture
def mock_connector_open_async(app, mocker):
    return mocker.patch.object(app.connector, "open_async", return_value=AsyncMock())


@pytest.fixture
def mock_connector_close_async(app, mocker):
    return mocker.patch.object(app.connector, "close_async", return_value=AsyncMock())


def test_enter_exit(not_opened_app, pool, mock_connector_open, mock_connector_close):

    with not_opened_app.open(pool) as app:
        pass

    mock_connector_open.assert_called_once_with(pool)
    mock_connector_close.assert_called_once_with()
    assert app is not_opened_app  # checks that open returns the app instance


def test_open(not_opened_app, pool, mock_connector_open):
    app = not_opened_app.open(pool)

    mock_connector_open.assert_called_once_with(pool)
    assert app is not_opened_app  # checks that open returns the app instance


def test_close(app, mock_connector_close):
    app.close()

    mock_connector_close.assert_called_once_with()


@pytest.mark.asyncio
async def test_async_enter_exit(
    not_opened_app, pool, mock_connector_open_async, mock_connector_close_async
):
    async with not_opened_app.open_async(pool) as app:
        pass

    mock_connector_open_async.assert_called_once_with(pool=pool)
    mock_connector_close_async.assert_called_once_with()
    assert app is not_opened_app  # checks that open_async returns the app instance


@pytest.mark.asyncio
async def test_open_async(not_opened_app, pool, mock_connector_open_async):
    app = await not_opened_app.open_async(pool)

    mock_connector_open_async.assert_called_once_with(pool=pool)
    assert app is not_opened_app  # checks that open_async returns the app instance


@pytest.mark.asyncio
async def test_close_async(app, mock_connector_close_async):

    await app.close_async()

    mock_connector_close_async.assert_called_once_with()
