import pytest

from cabbage import exceptions, postgres, task_worker, tasks


@pytest.fixture
def manager():
    return tasks.TaskManager(connection=object())


def test_run(manager, mocker):
    class TestTaskWorker(task_worker.Worker):
        i = 0

        def process_tasks(self):
            if self.i == 2:
                self.stop(None, None)
            self.i += 1

    listen_queue = mocker.patch("cabbage.postgres.listen_queue")
    select = mocker.patch("select.select")

    worker = TestTaskWorker(task_manager=manager, queue="marsupilami")

    worker.run(timeout=42)

    listen_queue.assert_called_with(connection=manager.connection, queue="marsupilami")
    select.assert_called_with([manager.connection], [], [], 42)


def test_process_tasks(mocker, manager):
    row1, row2, row3 = mocker.Mock(id=42), mocker.Mock(id=43), mocker.Mock(id=44)
    mocker.patch("cabbage.postgres.get_tasks", return_value=[row1, row2, row3])
    worker = task_worker.Worker(manager, "queue")

    i = 0

    def side_effect(task_row):
        nonlocal i
        i += 1
        if i == 1:
            # First time the task runs
            return None
        elif i == 2:
            # Then the task fails
            raise exceptions.TaskError()
        else:
            # While the third task runs, a stop signal is received
            worker.stop(None, None)

    call_task = mocker.patch(
        "cabbage.task_worker.Worker.run_task", side_effect=side_effect
    )
    finish_task = mocker.patch("cabbage.postgres.finish_task")

    worker.process_tasks()

    assert call_task.call_count == 3
    assert finish_task.call_count == 3

    assert call_task.call_args_list == [
        mocker.call(task_row=row1),
        mocker.call(task_row=row2),
        mocker.call(task_row=row3),
    ]

    assert finish_task.call_args_list == [
        mocker.call(manager.connection, 42, "done"),
        mocker.call(manager.connection, 43, "error"),
        mocker.call(manager.connection, 44, "done"),
    ]


def test_run_task(manager):
    result = []

    def job(a, b):  # pylint: disable=unused-argument
        result.append(a + b)

    task = tasks.Task(job, manager=manager, queue="yay", name="job")

    manager.tasks = {"job": task}

    row = postgres.TaskRow(
        id=16, args={"a": 9, "b": 3}, targeted_object="sherlock", task_type="job"
    )
    worker = task_worker.Worker(manager, "yay")
    worker.run_task(row)

    assert result == [12]


def test_run_task_error(manager):
    def job(a, b):  # pylint: disable=unused-argument
        raise ValueError("nope")

    task = tasks.Task(job, manager=manager, queue="yay", name="job")
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
