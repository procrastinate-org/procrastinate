import pytest

from cabbage import exceptions, postgres, task_worker, tasks


@pytest.fixture
def manager():
    return tasks.TaskManager(object())


def test_process_tasks(mocker, manager):
    row1, row2 = mocker.Mock(id=42), mocker.Mock(id=43)
    mocker.patch("cabbage.postgres.get_tasks", return_value=[row1, row2])
    call_task = mocker.patch(
        "cabbage.task_worker.Worker.run_task",
        side_effect=[None, exceptions.TaskError()],
    )
    finish_task = mocker.patch("cabbage.postgres.finish_task")

    worker = task_worker.Worker(manager, "queue")
    worker.process_tasks()

    assert call_task.call_count == 2
    assert finish_task.call_count == 2

    assert call_task.call_args_list == [
        mocker.call(task_row=row1),
        mocker.call(task_row=row2),
    ]

    assert finish_task.call_args_list == [
        mocker.call(manager.connection, 42, "done"),
        mocker.call(manager.connection, 43, "error"),
    ]


def test_run_task(manager):
    result = []

    def job(task_run, a, b):  # pylint: disable=unused-argument
        result.append(a + b)

    task = tasks.Task(manager=manager, queue="yay", name="job")
    task.func = job

    manager.tasks = {"job": task}

    row = postgres.TaskRow(
        id=16, args={"a": 9, "b": 3}, targeted_object="sherlock", task_type="job"
    )
    worker = task_worker.Worker(manager, "yay")
    worker.run_task(row)

    assert result == [12]


def test_run_task_error(manager):
    def job(task_run, a, b):  # pylint: disable=unused-argument
        raise ValueError("nope")

    task = tasks.Task(manager=manager, queue="yay", name="job")
    task.func = job

    manager.tasks = {"job": task}

    row = postgres.TaskRow(
        id=16, args={"a": 9, "b": 3}, targeted_object="sherlock", task_type="job"
    )
    worker = task_worker.Worker(manager, "yay")
    with pytest.raises(exceptions.TaskError):
        worker.run_task(row)


def test_run_task_not_found(manager):
    row = postgres.TaskRow(
        id=16, args={"a": 9, "b": 3}, targeted_object="sherlock", task_type="job"
    )
    worker = task_worker.Worker(manager, "yay")
    with pytest.raises(exceptions.TaskNotFound):
        worker.run_task(row)
