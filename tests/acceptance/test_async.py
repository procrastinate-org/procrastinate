from __future__ import annotations

import asyncio
import time

import pytest

from procrastinate import app as app_module
from procrastinate.contrib import aiopg
from procrastinate.exceptions import JobAborted
from procrastinate.jobs import Status


@pytest.fixture(params=["psycopg_connector", "aiopg_connector"])
async def async_app(request, psycopg_connector, connection_params):
    app = app_module.App(
        connector={
            "psycopg_connector": psycopg_connector,
            "aiopg_connector": aiopg.AiopgConnector(**connection_params),
        }[request.param]
    )
    async with app.open_async():
        yield app


async def test_defer(async_app):
    sum_results = []
    product_results = []

    @async_app.task(queue="default", name="sum_task")
    def sum_task(a, b):
        sum_results.append(a + b)

    @async_app.task(queue="default", name="product_task")
    async def product_task(a, b):
        product_results.append(a * b)

    await sum_task.defer_async(a=1, b=2)
    await sum_task.configure().defer_async(a=3, b=4)
    await async_app.configure_task(name="sum_task").defer_async(a=5, b=6)
    await product_task.defer_async(a=3, b=4)

    await async_app.run_worker_async(queues=["default"], wait=False)

    assert sum_results == [3, 7, 11]
    assert product_results == [12]


async def test_cancel(async_app):
    sum_results = []

    @async_app.task(queue="default", name="sum_task")
    async def sum_task(a, b):
        sum_results.append(a + b)

    job_id = await sum_task.defer_async(a=1, b=2)
    await sum_task.defer_async(a=3, b=4)

    result = await async_app.job_manager.cancel_job_by_id_async(job_id)
    assert result is True

    status = await async_app.job_manager.get_job_status_async(job_id)
    assert status == Status.CANCELLED

    jobs = await async_app.job_manager.list_jobs_async()
    assert len(jobs) == 2

    await async_app.run_worker_async(queues=["default"], wait=False)

    assert sum_results == [7]


async def test_cancel_with_delete(async_app):
    sum_results = []

    @async_app.task(queue="default", name="sum_task")
    async def sum_task(a, b):
        sum_results.append(a + b)

    job_id = await sum_task.defer_async(a=1, b=2)
    await sum_task.defer_async(a=3, b=4)

    result = await async_app.job_manager.cancel_job_by_id_async(job_id, delete_job=True)
    assert result is True

    jobs = await async_app.job_manager.list_jobs_async()
    assert len(jobs) == 1

    await async_app.run_worker_async(queues=["default"], wait=False)

    assert sum_results == [7]


async def test_no_job_to_cancel_found(async_app):
    @async_app.task(queue="default", name="example_task")
    def example_task():
        pass

    job_id = await example_task.defer_async()

    result = await async_app.job_manager.cancel_job_by_id_async(job_id + 1)
    assert result is False

    status = await async_app.job_manager.get_job_status_async(job_id)
    assert status == Status.TODO

    jobs = await async_app.job_manager.list_jobs_async()
    assert len(jobs) == 1


async def test_abort(async_app):
    @async_app.task(queue="default", name="task1", pass_context=True)
    async def task1(context):
        while True:
            await asyncio.sleep(0.02)
            if await context.should_abort_async():
                raise JobAborted

    @async_app.task(queue="default", name="task2", pass_context=True)
    def task2(context):
        while True:
            time.sleep(0.02)
            if context.should_abort():
                raise JobAborted

    job1_id = await task1.defer_async()
    job2_id = await task2.defer_async()

    worker_task = asyncio.create_task(
        async_app.run_worker_async(queues=["default"], wait=False)
    )

    await asyncio.sleep(0.05)
    result = await async_app.job_manager.cancel_job_by_id_async(job1_id, abort=True)
    assert result is True

    await asyncio.sleep(0.05)
    result = await async_app.job_manager.cancel_job_by_id_async(job2_id, abort=True)
    assert result is True

    await worker_task

    status = await async_app.job_manager.get_job_status_async(job1_id)
    assert status == Status.ABORTED

    status = await async_app.job_manager.get_job_status_async(job2_id)
    assert status == Status.ABORTED


async def test_retry_when_aborting(async_app):
    attempts = 0

    @async_app.task(queue="default", name="task1", pass_context=True, retry=True)
    async def example_task(context):
        nonlocal attempts
        attempts += 1
        await async_app.job_manager.cancel_job_by_id_async(context.job.id, abort=True)
        raise ValueError()

    job_id = await example_task.defer_async()

    await async_app.run_worker_async(queues=["default"], wait=False)

    status = await async_app.job_manager.get_job_status_async(job_id)
    assert status == Status.FAILED
    assert attempts == 1
