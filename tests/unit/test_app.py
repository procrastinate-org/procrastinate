from procrastinate import app as app_module
from procrastinate import tasks


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

    app._worker(queues=["yay"])

    Worker.assert_called_once_with(queues=["yay"], app=app)


def test_app_run_worker(app, mocker):
    run = mocker.patch("procrastinate.worker.Worker.run")

    app.run_worker(queues=["yay"])

    run.assert_called_once_with()


def test_app_run_worker_only_once(app):
    @app.task
    def yay():
        pass

    yay.defer()

    assert len(app.job_store.finished_jobs) == 0
    app.run_worker(only_once=True)
    assert len(app.job_store.finished_jobs) == 1


def test_from_path(mocker):
    load = mocker.patch("procrastinate.utils.load_from_path")
    assert app_module.App.from_path("dotted.path") is load.return_value
    load.assert_called_once_with("dotted.path", app_module.App)
