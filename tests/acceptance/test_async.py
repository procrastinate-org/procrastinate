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

    await async_app.job_manager.cancel_job_by_id_async(job_id)

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

    await async_app.job_manager.cancel_job_by_id_async(job_id, delete_job=True)

    jobs = await async_app.job_manager.list_jobs_async()
    assert len(jobs) == 1

    await async_app.run_worker_async(queues=["default"], wait=False)

    assert sum_results == [7]


async def test_abort(async_app):
    @async_app.task(queue="default", name="task1", pass_context=True)
    async def task1(context):
        while True:
            await asyncio.sleep(1)
            if await context.should_abort_async():
                raise JobAborted

    @async_app.task(queue="default", name="task2", pass_context=True)
    def task2(context):
        while True:
            time.sleep(1)
            if context.should_abort():
                raise JobAborted

    job1_id = await task1.defer_async()
    job2_id = await task2.defer_async()

    worker_task = asyncio.create_task(
        async_app.run_worker_async(queues=["default"], wait=False)
    )

    await asyncio.sleep(1)
    await async_app.job_manager.cancel_job_by_id_async(job1_id, abort=True)

    await asyncio.sleep(1)
    await async_app.job_manager.cancel_job_by_id_async(job2_id, abort=True)

    await worker_task

    status = await async_app.job_manager.get_job_status_async(job1_id)
    assert status == Status.ABORTED

    status = await async_app.job_manager.get_job_status_async(job2_id)
    assert status == Status.ABORTED
