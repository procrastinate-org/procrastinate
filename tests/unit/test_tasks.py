import uuid

import pytest

from cabbage import jobs, postgres, tasks, testing


@pytest.fixture
def manager(mocker):
    store = testing.InMemoryJobStore()
    return tasks.TaskManager(job_store=store)


def job():
    pass


def test_task_init_with_no_name(manager):
    task = tasks.Task(job, manager=manager, queue="queue")

    assert task.func is job
    assert task.name == "job"


def test_task_init_explicit_name(manager, mocker):
    task = tasks.Task(job, manager=manager, queue="queue", name="other")

    assert task.name == "other"


def test_task_defer(manager, mocker):
    manager.job_store.register_queue("queue")
    task = tasks.Task(job, manager=manager, queue="queue", name="job")

    task.defer(lock="sherlock", a="b", c=3)

    assert manager.job_store.jobs["queue"] == [
        jobs.Job(
            id=0,
            queue="queue",
            task_name="job",
            lock="sherlock",
            kwargs={"a": "b", "c": 3},
        )
    ]


def test_task_defer_no_lock(manager, mocker):
    manager.job_store.register_queue("queue")
    task = tasks.Task(job, manager=manager, queue="queue", name="job")

    task.defer(a="b", c=3)

    assert uuid.UUID(manager.job_store.jobs["queue"][0].lock)


def test_task_manager_task_explicit(manager, mocker):
    @manager.task(queue="a", name="b")
    def wrapped():
        return "foo"

    assert "foo" == wrapped()
    assert "b" == manager.tasks["b"].name
    assert "a" == manager.tasks["b"].queue
    assert manager.tasks["b"] is wrapped
    assert manager.tasks["b"].func is wrapped.__wrapped__


def test_task_manager_task_implicit(manager, mocker):
    @manager.task
    def wrapped():
        return "foo"

    assert "foo" == wrapped()
    assert "wrapped" == manager.tasks["wrapped"].name
    assert "default" == manager.tasks["wrapped"].queue
    assert manager.tasks["wrapped"] is wrapped
    assert manager.tasks["wrapped"].func is wrapped.__wrapped__


def test_task_manager_register(manager, mocker):
    task = tasks.Task(job, manager=manager, queue="queue", name="bla")

    manager.register(task)

    assert manager.queues == {"queue"}
    assert manager.tasks == {"bla": task}
    assert set(manager.job_store.jobs) == {"queue"}


def test_task_manager_register_queue_already_exists(manager, mocker):
    manager.queues.add("queue")
    task = tasks.Task(job, manager=manager, queue="queue", name="bla")

    manager.register(task)

    assert manager.queues == {"queue"}
    assert manager.tasks == {"bla": task}
    # We never told the store that there were queues to register
    assert not manager.job_store.jobs


def test_task_manager_default_connection(mocker):
    mocker.patch("cabbage.postgres.get_connection")
    manager = tasks.TaskManager()

    assert isinstance(manager.job_store, postgres.PostgresJobStore)


def test_task_manager_with_job_store_class():
    manager = tasks.TaskManager.with_job_store_class("cabbage.testing.InMemoryJobStore")

    assert isinstance(manager.job_store, testing.InMemoryJobStore)
