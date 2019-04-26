import uuid

import pytest

from cabbage import jobs, postgres, tasks, testing


@pytest.fixture
def task_manager(mocker):
    store = testing.InMemoryJobStore()
    return tasks.TaskManager(job_store=store)


def job():
    pass


def test_task_init_with_no_name(task_manager):
    task = tasks.Task(job, manager=task_manager, queue="queue")

    assert task.func is job
    assert task.name == "job"


def test_task_init_explicit_name(task_manager, mocker):
    task = tasks.Task(job, manager=task_manager, queue="queue", name="other")

    assert task.name == "other"


def test_task_defer(task_manager, mocker):
    task_manager.job_store.register_queue("queue")
    task = tasks.Task(job, manager=task_manager, queue="queue", name="job")

    task.defer(lock="sherlock", a="b", c=3)

    assert task_manager.job_store.jobs["queue"] == [
        jobs.Job(
            id=0,
            queue="queue",
            task_name="job",
            lock="sherlock",
            kwargs={"a": "b", "c": 3},
        )
    ]


def test_task_defer_no_lock(task_manager, mocker):
    task_manager.job_store.register_queue("queue")
    task = tasks.Task(job, manager=task_manager, queue="queue", name="job")

    task.defer(a="b", c=3)

    assert uuid.UUID(task_manager.job_store.jobs["queue"][0].lock)


def test_task_manager_task_explicit(task_manager, mocker):
    @manager.task(queue="a", name="b")
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

    assert "foo" == wrapped()
    assert "wrapped" == task_manager.tasks["wrapped"].name
    assert "default" == task_manager.tasks["wrapped"].queue
    assert task_manager.tasks["wrapped"] is wrapped
    assert task_manager.tasks["wrapped"].func is wrapped.__wrapped__


def test_task_manager_register(task_manager, mocker):
    task = tasks.Task(job, manager=task_manager, queue="queue", name="bla")

    task_manager.register(task)

    assert task_manager.queues == {"queue"}
    assert task_manager.tasks == {"bla": task}
    assert set(task_manager.job_store.jobs) == {"queue"}


def test_task_manager_register_queue_already_exists(task_manager, mocker):
    task_manager.queues.add("queue")
    task = tasks.Task(job, manager=task_manager, queue="queue", name="bla")

    task_manager.register(task)

    assert task_manager.queues == {"queue"}
    assert task_manager.tasks == {"bla": task}
    # We never told the store that there were queues to register
    assert not task_manager.job_store.jobs


def test_task_manager_default_connection(mocker):
    mocker.patch("cabbage.postgres.get_connection")
    task_manager = tasks.TaskManager()

    assert isinstance(task_manager.job_store, postgres.PostgresJobStore)


def test_task_manager_with_job_store_class():
    task_manager = tasks.TaskManager.with_job_store_class(
        "cabbage.testing.InMemoryJobStore"
    )

    assert isinstance(task_manager.job_store, testing.InMemoryJobStore)
