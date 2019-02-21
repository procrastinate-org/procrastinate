import uuid

import pytest
from cabbage import tasks


@pytest.fixture
def manager():
    return tasks.TaskManager()


def test_task_call(manager, mocker):

    register = mocker.patch("cabbage.tasks.TaskManager.register")
    task = tasks.Task(manager=manager, queue="queue")

    def job():
        pass

    assert task(job) is task

    assert task.func is job
    assert task.name == "job"
    register.assert_called_with(task)


def test_task_call_explicit_name(manager, mocker):

    mocker.patch("cabbage.tasks.TaskManager.register")
    task = tasks.Task(manager=manager, queue="queue", name="other")

    def job():
        pass

    task(job)

    assert task.name == "other"


def test_task_defer(manager, mocker):
    launch_task = mocker.patch("cabbage.postgres.launch_task")
    task = tasks.Task(manager=manager, queue="queue", name="job")

    task.defer(lock="sherlock", a="b", c=3)

    launch_task.assert_called_with(
        queue="queue", name="job", lock="sherlock", kwargs={"a": "b", "c": 3}
    )


def test_task_defer_no_lock(manager, mocker):
    launch_task = mocker.patch("cabbage.postgres.launch_task")
    task = tasks.Task(manager=manager, queue="queue", name="job")

    task.defer(a="b", c=3)

    _, kwargs = launch_task.call_args_list[0]
    # Will raise if not a correct uuid
    assert uuid.UUID(kwargs["lock"])


def test_task_defer_no_name(manager, mocker):
    mocker.patch("cabbage.postgres.launch_task")
    task = tasks.Task(manager=manager, queue="queue")

    with pytest.raises(AssertionError):
        task.defer(a="b", c=3)


def test_task_manager_task(manager):
    task = manager.task(queue="a", name="b")

    assert task.queue == "a"
    assert task.name == "b"
    assert task.manager is manager


def test_task_manager_register(manager, mocker):
    register_queue = mocker.patch("cabbage.postgres.register_queue")
    task = tasks.Task(manager=manager, queue="queue", name="bla")

    manager.register(task)

    assert manager.queues == {"queue"}
    assert manager.tasks == {"bla": task}
    register_queue.assert_called_with("queue")


def test_task_manager_register_no_task_name(manager, mocker):
    mocker.patch("cabbage.postgres.register_queue")

    task = tasks.Task(manager=manager, queue="queue")

    with pytest.raises(AssertionError):
        manager.register(task)


def test_task_manager_register_queue_already_exists(manager, mocker):
    register_queue = mocker.patch("cabbage.postgres.register_queue")
    manager.queues.add("queue")
    task = tasks.Task(manager=manager, queue="queue", name="bla")

    manager.register(task)

    assert manager.queues == {"queue"}
    assert manager.tasks == {"bla": task}
    register_queue.assert_not_called()


def test_task_run_run(manager, mocker):

    job = mocker.MagicMock()
    task = tasks.Task(manager=manager, queue="bla", name="foo")(job)
    task_run = tasks.TaskRun(task=task, id=12, lock="bla")
    task_run.run(a=1, b=2)

    job.assert_called_with(task_run, a=1, b=2)


def test_task_run_run_no_func(manager, mocker):

    task = tasks.Task(manager=manager, queue="bla", name="foo")
    task_run = tasks.TaskRun(task=task, id=12, lock="bla")

    with pytest.raises(AssertionError):
        task_run.run(a=1, b=2)
