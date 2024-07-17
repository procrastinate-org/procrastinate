from __future__ import annotations

import asyncio
from typing import cast

import pytest

from procrastinate.app import App
from procrastinate.jobs import Status
from procrastinate.testing import InMemoryConnector
from procrastinate.worker import Worker


@pytest.mark.parametrize(
    "available_jobs, concurrency",
    [
        (0, 1),
        (1, 1),
        (2, 1),
        (1, 2),
        (2, 2),
        (4, 2),
    ],
)
async def test_worker_run_no_wait(app: App, available_jobs, concurrency):
    worker = Worker(app, wait=False, concurrency=concurrency)

    @app.task
    async def perform_job():
        pass

    for i in range(available_jobs):
        await perform_job.defer_async()

    await asyncio.wait_for(worker.run(), 0.1)


async def test_worker_run_wait_until_cancelled(app: App):
    worker = Worker(app, wait=True)
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(worker.run(), 0.05)


async def test_worker_run_wait_stop(app: App, caplog):
    caplog.set_level("INFO")
    worker = Worker(app, wait=True)
    run_task = asyncio.create_task(worker.run())
    # wait just enough to make sure the task is running
    await asyncio.sleep(0.01)
    worker.stop()
    with pytest.raises(asyncio.CancelledError):
        await asyncio.wait_for(run_task, 0.1)

    assert set(caplog.messages) == {
        "Starting worker on all queues",
        "Stop requested",
        "Stopped worker on all queues",
        "No periodic task found, periodic deferrer will not run.",
    }


async def test_worker_run_once_log_messages(app: App, caplog):
    caplog.set_level("INFO")
    worker = Worker(app, wait=False)
    await asyncio.wait_for(worker.run(), 0.1)

    assert caplog.messages == [
        "Starting worker on all queues",
        "No job found. Stopping worker because wait=False",
        "Stopped worker on all queues",
    ]


async def test_worker_run_wait_listen(app: App):
    worker = Worker(app, wait=True, listen_notify=True, queues=["qq"])
    run_task = asyncio.create_task(worker.run())
    # wait just enough to make sure the task is running
    await asyncio.sleep(0.01)

    connector = cast(InMemoryConnector, app.connector)

    assert connector.notify_event
    assert connector.notify_channels == ["procrastinate_queue#qq"]

    run_task.cancel()
    try:
        await asyncio.wait_for(run_task, timeout=0.2)
    except asyncio.CancelledError:
        pass


@pytest.mark.parametrize(
    "available_jobs, concurrency",
    [
        (2, 1),
        (3, 2),
    ],
)
async def test_worker_run_respects_concurrency(app: App, available_jobs, concurrency):
    worker = Worker(app, wait=False, concurrency=concurrency)
    run_task = asyncio.create_task(worker.run())

    complete_tasks = asyncio.Event()

    @app.task
    async def perform_job():
        await complete_tasks.wait()

    for _ in range(available_jobs):
        await perform_job.defer_async()

    # wait just enough to make sure the task is running
    await asyncio.sleep(0.01)

    connector = cast(InMemoryConnector, app.connector)

    doings_jobs = list(connector.list_jobs_all(status=Status.DOING.value))
    todo_jobs = list(connector.list_jobs_all(status=Status.TODO.value))

    assert len(doings_jobs) == concurrency
    assert len(todo_jobs) == available_jobs - concurrency

    complete_tasks.set()
    await asyncio.wait_for(run_task, 0.1)


async def test_worker_run_fetches_job_on_notification(app: App):
    worker = Worker(app, wait=True, concurrency=1)

    run_task = asyncio.create_task(worker.run())

    complete_tasks = asyncio.Event()

    @app.task
    async def perform_job():
        await complete_tasks.wait()

    await asyncio.sleep(0.01)

    connector = cast(InMemoryConnector, app.connector)

    assert len([query for query in connector.queries if query[0] == "fetch_job"]) == 1

    await asyncio.sleep(0.01)

    assert len([query for query in connector.queries if query[0] == "fetch_job"]) == 1

    await perform_job.defer_async()
    await asyncio.sleep(0.01)

    assert len([query for query in connector.queries if query[0] == "fetch_job"]) == 2

    complete_tasks.set()
    run_task.cancel()
    try:
        await asyncio.wait_for(run_task, timeout=0.2)
    except asyncio.CancelledError:
        pass


async def test_worker_run_respects_polling(app: App):
    worker = Worker(app, wait=True, concurrency=1, timeout=0.05)

    run_task = asyncio.create_task(worker.run())

    await asyncio.sleep(0.01)

    connector = cast(InMemoryConnector, app.connector)
    assert len([query for query in connector.queries if query[0] == "fetch_job"]) == 1

    await asyncio.sleep(0.05)

    assert len([query for query in connector.queries if query[0] == "fetch_job"]) == 2
    run_task.cancel()
    try:
        await asyncio.wait_for(run_task, timeout=0.2)
    except asyncio.CancelledError:
        pass
