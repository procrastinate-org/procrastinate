from __future__ import annotations

import asyncio
import time

import pytest
from asgiref.sync import sync_to_async

import procrastinate
from procrastinate.contrib import psycopg2
from procrastinate.jobs import Status


@pytest.fixture(params=["sync_psycopg_connector", "psycopg2_connector"])
async def sync_app(request, sync_psycopg_connector, connection_params):
    app = procrastinate.App(
        connector={
            "sync_psycopg_connector": sync_psycopg_connector,
            "psycopg2_connector": psycopg2.Psycopg2Connector(**connection_params),
        }[request.param]
    )

    with app.open():
        yield app


@pytest.fixture
async def async_app(not_opened_psycopg_connector):
    app = procrastinate.App(connector=not_opened_psycopg_connector)
    async with app.open_async():
        yield app


# Even if we test the purely sync parts, we'll still need an async worker to execute
# the tasks
async def test_defer(sync_app: procrastinate.App, async_app: procrastinate.App):
    sum_results = []
    product_results = []

    @sync_app.task(queue="default", name="sum_task")
    def sum_task(a, b):
        sum_results.append(a + b)

    @sync_app.task(queue="default", name="product_task")
    async def product_task(a, b):
        product_results.append(a * b)

    sum_task.defer(a=1, b=2)
    sum_task.configure().defer(a=3, b=4)
    sync_app.configure_task(name="sum_task").defer(a=5, b=6)
    product_task.defer(a=3, b=4)

    # We need to run the async app to execute the tasks
    async_app.tasks = sync_app.tasks
    await async_app.run_worker_async(queues=["default"], wait=False)

    assert sum_results == [3, 7, 11]
    assert product_results == [12]


async def test_nested_sync_to_async(
    sync_app: procrastinate.App, async_app: procrastinate.App
):
    sum_results = []

    @sync_app.task(queue="default", name="sum_task")
    def sum_task_sync(a, b):
        async def _sum_task_async(a, b):
            def _inner_sum_task_sync(a, b):
                sum_results.append(a + b)

            # Only works if the worker runs the sync task in a separate thread
            await sync_to_async(_inner_sum_task_sync)(a, b)

        asyncio.run(_sum_task_async(a, b))

    sum_task_sync.defer(a=1, b=2)

    # We need to run the async app to execute the tasks
    async_app.tasks = sync_app.tasks
    await async_app.run_worker_async(queues=["default"], wait=False)

    assert sum_results == [3]


async def test_sync_task_runs_in_parallel(
    sync_app: procrastinate.App, async_app: procrastinate.App
):
    results = []

    @sync_app.task(queue="default", name="sync_task_1")
    def sync_task_1():
        for i in range(3):
            time.sleep(0.1)
            results.append(i)

    @sync_app.task(queue="default", name="sync_task_2")
    def sync_task_2():
        for i in range(3):
            time.sleep(0.1)
            results.append(i)

    sync_task_1.defer()
    sync_task_2.defer()

    async_app.tasks = sync_app.tasks
    await async_app.run_worker_async(queues=["default"], concurrency=2, wait=False)

    assert results == [0, 0, 1, 1, 2, 2]


async def test_cancel(sync_app: procrastinate.App, async_app: procrastinate.App):
    sum_results = []

    @sync_app.task(queue="default", name="sum_task")
    def sum_task(a, b):
        sum_results.append(a + b)

    job_id = sum_task.defer(a=1, b=2)
    sum_task.defer(a=3, b=4)

    result = sync_app.job_manager.cancel_job_by_id(job_id)
    assert result is True

    status = sync_app.job_manager.get_job_status(job_id)
    assert status == Status.CANCELLED

    jobs = sync_app.job_manager.list_jobs()
    assert len(jobs) == 2

    # We need to run the async app to execute the tasks
    async_app.tasks = sync_app.tasks
    await async_app.run_worker_async(queues=["default"], wait=False)

    assert sum_results == [7]


def test_no_job_to_cancel_found(sync_app: procrastinate.App):
    @sync_app.task(queue="default", name="example_task")
    def example_task():
        pass

    job_id = example_task.defer()

    result = sync_app.job_manager.cancel_job_by_id(job_id + 1)
    assert result is False

    status = sync_app.job_manager.get_job_status(job_id)
    assert status == Status.TODO

    jobs = sync_app.job_manager.list_jobs()
    assert len(jobs) == 1
