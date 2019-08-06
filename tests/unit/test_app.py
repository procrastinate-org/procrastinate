import pytest

from cabbage import app, postgres, tasks, testing


def task_func():
    pass


def test_app_task_explicit(app, mocker):
    @app.task(queue="a", name="b")
    def wrapped():
        return "foo"

    assert "foo" == wrapped()
    assert "b" == app.tasks["b"].name
    assert "a" == app.tasks["b"].queue
    assert app.tasks["b"] is wrapped
    assert app.tasks["b"].func is wrapped.__wrapped__


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


def test_app_register(app, mocker):
    task = tasks.Task(task_func, app=app, queue="queue", name="bla")

    app._register(task)

    assert app.queues == {"queue"}
    assert app.tasks == {"bla": task}


def test_app_register_queue_already_exists(app, mocker):
    app.queues.add("queue")
    task = tasks.Task(task_func, app=app, queue="queue", name="bla")

    app._register(task)

    assert app.queues == {"queue"}
    assert app.tasks == {"bla": task}


@pytest.mark.parametrize(
    "kwargs, store_class",
    [
        ({"in_memory": True}, testing.InMemoryJobStore),
        ({"in_memory": False}, postgres.PostgresJobStore),
        ({}, postgres.PostgresJobStore),
    ],
)
def test_app_job_store(mocker, kwargs, store_class):
    mocker.patch("cabbage.postgres.get_connection")
    cabbage_app = app.App(**kwargs)

    assert isinstance(cabbage_app.job_store, store_class)


def test_app_job_store_postgres_dsn(mocker):
    get_connection = mocker.patch("cabbage.postgres.get_connection")
    app.App(postgres_dsn="foo")

    get_connection.assert_called_once_with(dsn="foo")


def test_app_worker_default_params(mocker):
    cabbage_app = app.App(in_memory=True)
    Worker = mocker.patch("cabbage.worker.Worker")

    cabbage_app._worker()

    Worker.assert_called_once_with(import_paths=None, queues=None, app=cabbage_app)


def test_app_worker(mocker):
    cabbage_app = app.App(in_memory=True, import_paths=["json", "os", "sys"])
    Worker = mocker.patch("cabbage.worker.Worker")

    cabbage_app._worker(queues=["yay"])

    Worker.assert_called_once_with(
        import_paths=["json", "os", "sys"], queues=["yay"], app=cabbage_app
    )


def test_app_run_worker(mocker):
    run = mocker.patch("cabbage.worker.Worker.run")
    cabbage_app = app.App(in_memory=True, worker_timeout=42)

    cabbage_app.run_worker(queues=["yay"])

    run.assert_called_once_with(timeout=42)


def test_app_run_worker_only_once():
    cabbage_app = app.App(in_memory=True)

    @cabbage_app.task
    def yay():
        pass

    yay.defer()

    assert len(cabbage_app.job_store.finished_jobs) == 0
    cabbage_app.run_worker(only_once=True)
    assert len(cabbage_app.job_store.finished_jobs) == 1
