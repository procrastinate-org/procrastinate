import pytest

from cabbage import task_worker, tasks, exceptions


@pytest.fixture
def manager():
    return tasks.TaskManager()


# worker() is not unit-tested because we haven't found a
# way to unit-test it that brings anything to the table.
# If you do, feel free !
# It's tested in integration though


def test_infinite_loop():
    # Ok we're not testing up until infinity
    a = iter(range(10))

    with pytest.raises(StopIteration):
        task_worker.infinite_loop(a.__next__)


def test_one_loop(manager, mocker):
    # this test is not 100% useful but at least we're preventing accidental breakage
    process_task = mocker.patch("cabbage.task_worker.process_tasks")
    select = mocker.patch("select.select")
    cursor = mocker.Mock()

    task_worker.one_loop(task_manager=manager, queue="queue", curs=cursor, timeout=42)

    process_task.assert_called_with(task_manager=manager, queue="queue", curs=cursor)
    select.assert_called_with([cursor.connection], [], [], 42)


def test_process_task(mocker, manager):
    mocker.patch(
        "cabbage.postgres.get_tasks",
        return_value=[{"id": 42}, {"id": 43}, {"id": None}],
    )
    call_task = mocker.patch(
        "cabbage.task_worker.call_task", side_effect=[None, exceptions.TaskError()]
    )
    finish_task = mocker.patch("cabbage.postgres.finish_task")

    task_worker.process_tasks(task_manager=manager, queue="queue", curs="Monkey Island")

    assert call_task.call_count == 2
    assert finish_task.call_count == 2

    assert call_task.call_args_list == [
        mocker.call(task_manager=manager, task_row={"id": 42}),
        mocker.call(task_manager=manager, task_row={"id": 43}),
    ]

    assert finish_task.call_args_list == [
        mocker.call(cursor="Monkey Island", task_id=42, state="done"),
        mocker.call(cursor="Monkey Island", task_id=43, state="error"),
    ]


def test_call_task(manager):
    result = []

    def job(task_run, a, b):  # pylint: disable=unused-argument
        result.append(a + b)

    task = tasks.Task(manager=manager, queue="yay", name="job")
    task.func = job

    manager.tasks = {"job": task}

    row = {
        "id": 16,
        "args": {"a": 9, "b": 3},
        "targeted_object": "sherlock",
        "task_type": "job",
    }
    task_worker.call_task(task_manager=manager, task_row=row)

    assert result == [12]


def test_call_task_error(manager):
    def job(task_run, a, b):  # pylint: disable=unused-argument
        raise ValueError("nope")

    task = tasks.Task(manager=manager, queue="yay", name="job")
    task.func = job

    manager.tasks = {"job": task}

    row = {
        "id": 16,
        "args": {"a": 9, "b": 3},
        "targeted_object": "sherlock",
        "task_type": "job",
    }
    with pytest.raises(exceptions.TaskError):
        task_worker.call_task(task_manager=manager, task_row=row)


def test_call_task_not_found(manager):
    row = {
        "id": 16,
        "args": {"a": 9, "b": 3},
        "targeted_object": "sherlock",
        "task_type": "job",
    }
    with pytest.raises(exceptions.TaskNotFound):
        task_worker.call_task(task_manager=manager, task_row=row)
