import uuid

import pendulum
import pytest

from procrastinate import exceptions, jobs, tasks


def task_func():
    pass


def test_task_init_with_no_name(app):
    task = tasks.Task(task_func, app=app, queue="queue")

    assert task.func is task_func
    assert task.name == "tests.unit.test_tasks.task_func"


def test_task_init_explicit_name(app, mocker, caplog):
    task = tasks.Task(task_func, app=app, queue="queue", name="other")

    assert task.name == "other"

    assert [
        record
        for record in caplog.records
        if record.action == "task_name_differ_from_path"
    ]


def test_task_defer(app):
    task = tasks.Task(task_func, app=app, queue="queue")

    task.defer(c=3)

    # The lock is the only thing we can't predict
    lock = app.job_store.jobs[0].lock
    assert app.job_store.jobs == [
        jobs.Job(
            id=0,
            queue="queue",
            task_name="tests.unit.test_tasks.task_func",
            lock=lock,
            task_kwargs={"c": 3},
            job_store=app.job_store,
        )
    ]


def test_task_configure(app):
    task = tasks.Task(task_func, app=app, queue="queue")

    job = task.configure(lock="sher", task_kwargs={"yay": "ho"})

    assert job.lock == "sher"
    assert job.task_kwargs == {"yay": "ho"}


def test_task_configure_no_lock(app):
    task = tasks.Task(task_func, app=app, queue="queue")

    job = task.configure()

    assert uuid.UUID(job.lock)


def test_task_configure_schedule_at(app):
    task = tasks.Task(task_func, app=app, queue="queue")

    job = task.configure(schedule_at=pendulum.datetime(2000, 1, 1, tz="Europe/Paris"))

    assert job.scheduled_at == pendulum.datetime(2000, 1, 1, tz="Europe/Paris")


def test_task_configure_schedule_in(app):
    task = tasks.Task(task_func, app=app, queue="queue")

    now = pendulum.datetime(2000, 1, 1, tz="Europe/Paris")
    with pendulum.test(now):
        job = task.configure(schedule_in={"hours": 2})

    assert job.scheduled_at == pendulum.datetime(2000, 1, 1, 2, tz="Europe/Paris")


def test_task_configure_schedule_in_and_schedule_at(app):
    task = tasks.Task(task_func, app=app, queue="queue")

    with pytest.raises(ValueError):
        task.configure(
            schedule_at=pendulum.datetime(2000, 1, 1, tz="Europe/Paris"),
            schedule_in={"hours": 2},
        )


def test_task_get_retry_exception_none(app):
    task = tasks.Task(task_func, app=app, queue="queue")
    job = task.configure()

    assert task.get_retry_exception(job) is None


def test_task_get_retry_exception(app, mocker):
    mock = mocker.patch("procrastinate.retry.RetryStrategy.get_retry_exception")

    task = tasks.Task(task_func, app=app, queue="queue", retry=10)
    job = task.configure()

    assert task.get_retry_exception(job) is mock.return_value
    mock.assert_called_with(0)


def test_load_task_not_found():
    with pytest.raises(exceptions.TaskNotFound):
        tasks.load_task("foobarbaz")


def test_load_task_not_a_task():
    with pytest.raises(exceptions.TaskNotFound):
        tasks.load_task("json.loads")


some_task = None


def test_load_task(app):
    global some_task

    @app.task
    def task_func():
        return "foo"

    some_task = task_func

    assert tasks.load_task("tests.unit.test_tasks.some_task") == some_task
