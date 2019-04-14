import uuid

import pytest

from cabbage import tasks


@pytest.fixture
def manager():
    return tasks.TaskManager(object())


def job():
    pass


def test_task_init_with_no_name(manager):
    task = tasks.Task(job, manager=manager, queue="queue")

    assert task.func is job
    assert task.name == "job"


def test_task_init_explicit_name(manager, mocker):
    mocker.patch("cabbage.tasks.TaskManager.register")
    task = tasks.Task(job, manager=manager, queue="queue", name="other")

    assert task.name == "other"


def test_task_defer(manager, mocker):
    launch_task = mocker.patch("cabbage.postgres.launch_task")
    task = tasks.Task(job, manager=manager, queue="queue", name="job")

    task.defer(lock="sherlock", a="b", c=3)

    launch_task.assert_called_with(
        manager.connection,
        queue="queue",
        name="job",
        lock="sherlock",
        kwargs={"a": "b", "c": 3},
    )


def test_task_defer_no_lock(manager, mocker):
    launch_task = mocker.patch("cabbage.postgres.launch_task")
    task = tasks.Task(job, manager=manager, queue="queue", name="job")

    task.defer(a="b", c=3)

    _, kwargs = launch_task.call_args_list[0]
    # Will raise if not a correct uuid
    assert uuid.UUID(kwargs["lock"])


def test_task_manager_task_explicit(manager, mocker):
    mocker.patch("cabbage.postgres.register_queue")

    @manager.task(queue="a", name="b")
    def wrapped():
        return "foo"

    assert "foo" == wrapped()
    assert "b" == manager.tasks["b"].name
    assert "a" == manager.tasks["b"].queue
    assert manager.tasks["b"].func is wrapped


def test_task_manager_task_implicit(manager, mocker):
    mocker.patch("cabbage.postgres.register_queue")

    @manager.task
    def wrapped():
        return "foo"

    assert "foo" == wrapped()
    assert "wrapped" == manager.tasks["wrapped"].name
    assert "default" == manager.tasks["wrapped"].queue
    assert manager.tasks["wrapped"].func is wrapped


def test_task_manager_register(manager, mocker):
    register_queue = mocker.patch("cabbage.postgres.register_queue")
    task = tasks.Task(job, manager=manager, queue="queue", name="bla")

    manager.register(task)

    assert manager.queues == {"queue"}
    assert manager.tasks == {"bla": task}
    register_queue.assert_called_with(manager.connection, "queue")


def test_task_manager_register_queue_already_exists(manager, mocker):
    register_queue = mocker.patch("cabbage.postgres.register_queue")
    manager.queues.add("queue")
    task = tasks.Task(job, manager=manager, queue="queue", name="bla")

    manager.register(task)

    assert manager.queues == {"queue"}
    assert manager.tasks == {"bla": task}
    register_queue.assert_not_called()


def test_task_manager_default_connection(mocker):
    get_connection = mocker.patch("cabbage.postgres.get_connection")
    manager = tasks.TaskManager()

    assert manager.connection is get_connection.return_value
