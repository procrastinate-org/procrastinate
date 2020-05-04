import asyncio

import pytest

from procrastinate import exceptions, worker


@pytest.fixture
def test_worker(app):
    return worker.Worker(app=app, queues=["yay"])


def test_worker_load_task_known_missing(test_worker):
    test_worker.known_missing_tasks.add("foobarbaz")
    with pytest.raises(exceptions.TaskNotFound):
        test_worker.load_task("foobarbaz", log_context={})


def test_worker_load_task_known_task(app, test_worker):
    @app.task
    def task_func():
        pass

    assert (
        test_worker.load_task("tests.unit.test_worker_sync.task_func", log_context={})
        == task_func
    )


def test_worker_load_task_new_missing(test_worker):

    with pytest.raises(exceptions.TaskNotFound):
        test_worker.load_task("foobarbaz", log_context={})

    assert test_worker.known_missing_tasks == {"foobarbaz"}


unknown_task = None


def test_worker_load_task_unknown_task(app, caplog):
    global unknown_task
    test_worker = worker.Worker(app=app, queues=["yay"])

    @app.task
    def task_func():
        pass

    unknown_task = task_func

    assert (
        test_worker.load_task(
            "tests.unit.test_worker_sync.unknown_task", log_context={}
        )
        == task_func
    )

    assert [record for record in caplog.records if record.action == "load_dynamic_task"]


@pytest.mark.parametrize(
    "queues, result", [(None, "all queues"), (["foo", "bar"], "queues foo, bar")]
)
def test_queues_display(queues, result):
    assert worker.queues_display(queues) == result


def test_stop(test_worker, caplog):
    caplog.set_level("INFO")
    test_worker.notify_event = asyncio.Event()

    test_worker.stop()

    assert test_worker.stop_requested is True
    assert test_worker.notify_event.is_set()
    assert caplog.messages == ["Stop requested, no job to finish"]


def test_stop_log_job(test_worker, caplog):
    caplog.set_level("INFO")
    test_worker.current_job_context = {"call_string": "yay()"}
    test_worker.notify_event = asyncio.Event()

    test_worker.stop()

    assert test_worker.stop_requested is True
    assert test_worker.notify_event.is_set()
    assert caplog.messages == ["Stop requested, waiting for job to finish: yay()"]
