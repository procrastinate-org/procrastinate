import uuid

import pendulum
import pytest

from cabbage import exceptions, jobs, postgres, tasks


def task_func():
    pass


def test_task_init_with_no_name(task_manager):
    task = tasks.Task(task_func, manager=task_manager, queue="queue")

    assert task.func is task_func
    assert task.name == "tests.unit.test_tasks.task_func"


def test_task_init_explicit_name(task_manager, mocker, caplog):
    task = tasks.Task(task_func, manager=task_manager, queue="queue", name="other")

    assert task.name == "other"

    assert [
        record
        for record in caplog.records
        if record.action == "task_name_differ_from_path"
    ]


def test_task_defer(task_manager):
    task_manager.job_store.register_queue("queue")
    task = tasks.Task(task_func, manager=task_manager, queue="queue")

    task.defer(c=3)

    # The lock is the only thing we can't predict
    lock = task_manager.job_store.jobs["queue"][0].lock
    assert task_manager.job_store.jobs["queue"] == [
        jobs.Job(
            id=0,
            queue="queue",
            task_name="tests.unit.test_tasks.task_func",
            lock=lock,
            task_kwargs={"c": 3},
            job_store=task_manager.job_store,
        )
    ]


def test_task_configure(task_manager):
    task = tasks.Task(task_func, manager=task_manager, queue="queue")

    job = task.configure(lock="sher", task_kwargs={"yay": "ho"})

    assert job.lock == "sher"
    assert job.task_kwargs == {"yay": "ho"}


def test_task_configure_no_lock(task_manager):
    task = tasks.Task(task_func, manager=task_manager, queue="queue")

    job = task.configure()

    assert uuid.UUID(job.lock)


def test_task_configure_schedule_at(task_manager):
    task = tasks.Task(task_func, manager=task_manager, queue="queue")

    job = task.configure(schedule_at=pendulum.datetime(2000, 1, 1, tz="Europe/Paris"))

    assert job.scheduled_at == pendulum.datetime(2000, 1, 1, tz="Europe/Paris")


def test_task_configure_schedule_in(task_manager):
    task = tasks.Task(task_func, manager=task_manager, queue="queue")

    now = pendulum.datetime(2000, 1, 1, tz="Europe/Paris")
    with pendulum.test(now):
        job = task.configure(schedule_in={"hours": 2})

    assert job.scheduled_at == pendulum.datetime(2000, 1, 1, 2, tz="Europe/Paris")


def test_task_configure_schedule_in_and_schedule_at(task_manager):
    task = tasks.Task(task_func, manager=task_manager, queue="queue")

    with pytest.raises(ValueError):
        task.configure(
            schedule_at=pendulum.datetime(2000, 1, 1, tz="Europe/Paris"),
            schedule_in={"hours": 2},
        )


def test_task_manager_task_explicit(task_manager, mocker):
    @task_manager.task(queue="a", name="b")
    def wrapped():
        return "foo"

    assert "foo" == wrapped()
    assert "b" == task_manager.tasks["b"].name
    assert "a" == task_manager.tasks["b"].queue
    assert task_manager.tasks["b"] is wrapped
    assert task_manager.tasks["b"].func is wrapped.__wrapped__


def test_task_manager_task_implicit(task_manager, mocker):
    @task_manager.task
    def wrapped():
        return "foo"

    registered_task = task_manager.tasks["tests.unit.test_tasks.wrapped"]

    assert "foo" == wrapped()
    assert "tests.unit.test_tasks.wrapped" == registered_task.name
    assert "default" == registered_task.queue
    assert registered_task is wrapped
    assert registered_task.func is wrapped.__wrapped__


def test_task_manager_register(task_manager, mocker):
    task = tasks.Task(task_func, manager=task_manager, queue="queue", name="bla")

    task_manager.register(task)

    assert task_manager.queues == {"queue"}
    assert task_manager.tasks == {"bla": task}
    assert set(task_manager.job_store.jobs) == {"queue"}


def test_task_manager_register_queue_already_exists(task_manager, mocker):
    task_manager.queues.add("queue")
    task = tasks.Task(task_func, manager=task_manager, queue="queue", name="bla")

    task_manager.register(task)

    assert task_manager.queues == {"queue"}
    assert task_manager.tasks == {"bla": task}
    # We never told the store that there were queues to register
    assert not task_manager.job_store.jobs


def test_task_manager_default_connection(mocker):
    mocker.patch("cabbage.postgres.get_connection")
    task_manager = tasks.TaskManager()

    assert isinstance(task_manager.job_store, postgres.PostgresJobStore)


def test_load_task_not_found():
    with pytest.raises(exceptions.TaskNotFound):
        tasks.load_task("foobarbaz")


def test_load_task_not_a_task():
    with pytest.raises(exceptions.NotATask):
        tasks.load_task("json.loads")


some_task = None


def test_load_task(task_manager):
    global some_task

    @task_manager.task
    def task_func():
        return "foo"

    some_task = task_func

    assert tasks.load_task("tests.unit.test_tasks.some_task") == some_task
