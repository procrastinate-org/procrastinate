from cabbage import app, postgres, tasks


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

    app.register(task)

    assert app.queues == {"queue"}
    assert app.tasks == {"bla": task}


def test_app_register_queue_already_exists(app, mocker):
    app.queues.add("queue")
    task = tasks.Task(task_func, app=app, queue="queue", name="bla")

    app.register(task)

    assert app.queues == {"queue"}
    assert app.tasks == {"bla": task}


def test_app_default_connection(mocker):
    mocker.patch("cabbage.postgres.get_connection")
    cabbage_app = app.App()

    assert isinstance(cabbage_app.job_store, postgres.PostgresJobStore)
