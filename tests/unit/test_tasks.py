import pytest

from procrastinate import exceptions, tasks, utils

from .. import conftest


def task_func():
    pass


def test_task_init_with_no_name(app):
    task = tasks.Task(task_func, app=app, queue="queue")

    assert task.func is task_func
    assert task.name == "tests.unit.test_tasks.task_func"


@pytest.mark.asyncio
async def test_task_defer_async(app, connector):
    task = tasks.Task(task_func, app=app, queue="queue")

    await task.defer_async(c=3)

    # The lock is the only thing we can't predict
    lock = connector.jobs[1]["lock"]
    assert connector.jobs == {
        1: {
            "id": 1,
            "queue_name": "queue",
            "task_name": "tests.unit.test_tasks.task_func",
            "lock": lock,
            "queueing_lock": None,
            "args": {"c": 3},
            "status": "todo",
            "scheduled_at": None,
            "attempts": 0,
        }
    }


def test_configure_task(job_store):
    job = tasks.configure_task(
        name="my_name", job_store=job_store, lock="sher", task_kwargs={"yay": "ho"}
    ).job

    assert job.lock == "sher"
    assert job.task_kwargs == {"yay": "ho"}


def test_configure_task_schedule_at(job_store):
    job = tasks.configure_task(
        name="my_name",
        job_store=job_store,
        schedule_at=conftest.aware_datetime(2000, 1, 1, tz_offset=1),
    ).job

    assert job.scheduled_at == conftest.aware_datetime(2000, 1, 1, tz_offset=1)


def test_configure_task_schedule_in(job_store, mocker):
    now = conftest.aware_datetime(2000, 1, 1, tz_offset=1)
    mocker.patch.object(utils, "utcnow", return_value=now)
    job = tasks.configure_task(
        name="my_name", job_store=job_store, schedule_in={"hours": 2}
    ).job

    assert job.scheduled_at == conftest.aware_datetime(2000, 1, 1, 2, tz_offset=1)


def test_configure_task_schedule_in_and_schedule_at(job_store):
    with pytest.raises(ValueError):
        tasks.configure_task(
            name="my_name",
            job_store=job_store,
            schedule_at=conftest.aware_datetime(2000, 1, 1, tz_offset=1),
            schedule_in={"hours": 2},
        )


def test_task_configure(app):
    task = tasks.Task(task_func, app=app, queue="queue")

    job = task.configure(lock="sher", task_kwargs={"yay": "ho"}).job

    assert job.task_name == "tests.unit.test_tasks.task_func"
    assert job.lock == "sher"
    assert job.task_kwargs == {"yay": "ho"}
    assert job.queue == "queue"


def test_task_configure_override_queue(app):
    task = tasks.Task(task_func, app=app, queue="queue")

    job = task.configure(queue="other_queue").job

    assert job.queue == "other_queue"


def test_task_get_retry_exception_none(app):
    task = tasks.Task(task_func, app=app, queue="queue")
    job = task.configure().job

    assert task.get_retry_exception(exception=None, job=job) is None


def test_task_get_retry_exception(app, mocker):
    mock = mocker.patch("procrastinate.retry.RetryStrategy.get_retry_exception")

    task = tasks.Task(task_func, app=app, queue="queue", retry=10)
    job = task.configure().job

    exception = ValueError()
    assert task.get_retry_exception(exception=exception, job=job) is mock.return_value
    mock.assert_called_with(exception=exception, attempts=0)


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
