from __future__ import annotations

import pytest

import procrastinate
from procrastinate.contrib import psycopg2


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


@pytest.mark.benchmark
def test_benchmark_1000_sync_jobs(
    aio_benchmark, sync_app: procrastinate.App, async_app: procrastinate.App
):
    @sync_app.task(queue="default", name="sum_task")
    def simple_task():
        pass

    async def defer_and_process_jobs():
        for _ in range(1000):
            simple_task.defer()

        await async_app.run_worker_async(queues=["default"], wait=False)

    aio_benchmark(defer_and_process_jobs)


@pytest.mark.benchmark
def test_benchmark_1000_sync_batch_jobs(
    aio_benchmark, sync_app: procrastinate.App, async_app: procrastinate.App
):
    @sync_app.task(queue="default", name="sum_task")
    def simple_task():
        pass

    async def defer_and_process_jobs():
        simple_task.batch_defer(*[{} for _ in range(1000)])

        await async_app.run_worker_async(queues=["default"], wait=False)

    aio_benchmark(defer_and_process_jobs)
