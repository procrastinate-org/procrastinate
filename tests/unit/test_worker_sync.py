from __future__ import annotations

import pytest

from procrastinate import exceptions, job_context, worker
from procrastinate.app import App


@pytest.fixture
def test_worker(app: App) -> worker.Worker:
    return worker.Worker(app=app, queues=["yay"])


@pytest.fixture
def context():
    return job_context.JobContext()


def test_worker_find_task_missing(test_worker):
    with pytest.raises(exceptions.TaskNotFound):
        test_worker.find_task("foobarbaz")


def test_worker_find_task(app: App):
    test_worker = worker.Worker(app=app, queues=["yay"])

    @app.task(name="foo")
    def task_func():
        pass

    assert test_worker.find_task("foo") == task_func


def test_stop(test_worker, caplog):
    caplog.set_level("INFO")

    test_worker.stop()

    assert caplog.messages == ["Stop requested"]
