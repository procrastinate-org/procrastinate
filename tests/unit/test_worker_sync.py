from __future__ import annotations

import asyncio

import pytest

from procrastinate import exceptions, job_context, worker


@pytest.fixture
def test_worker(app):
    return worker.Worker(app=app, queues=["yay"])


@pytest.fixture
def context():
    return job_context.JobContext()


def test_worker_find_task_missing(test_worker):
    with pytest.raises(exceptions.TaskNotFound):
        test_worker.find_task("foobarbaz")


def test_worker_find_task(app):
    test_worker = worker.Worker(app=app, queues=["yay"])

    @app.task(name="foo")
    def task_func():
        pass

    assert test_worker.find_task("foo") == task_func


def test_stop(test_worker, caplog):
    caplog.set_level("INFO")
    test_worker.notify_event = asyncio.Event()

    test_worker.stop()

    assert test_worker.stop_requested is True
    assert test_worker.notify_event.is_set()
    assert caplog.messages == ["Stop requested"]


def test_stop_log_job(test_worker, caplog, context, job_factory):
    caplog.set_level("INFO")
    test_worker.notify_event = asyncio.Event()
    job = job_factory(id=42, task_name="bla")
    ctx = context.evolve(job=job, worker_id=0)
    test_worker.current_contexts[0] = ctx

    test_worker.stop()

    assert test_worker.stop_requested is True
    assert test_worker.notify_event.is_set()
    assert caplog.messages == [
        "Stop requested",
        "Waiting for job to finish: worker 0: bla[42]()",
    ]
