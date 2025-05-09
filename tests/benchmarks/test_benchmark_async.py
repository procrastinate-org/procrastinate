from __future__ import annotations

import pytest

from procrastinate import app as app_module
from procrastinate.contrib import aiopg


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


@pytest.mark.benchmark
def test_benchmark_1000_async_jobs(aio_benchmark, async_app: app_module.App):
    @async_app.task(queue="default", name="simple_task")
    async def simple_task():
        pass

    async def defer_and_process_jobs():
        for _ in range(1000):
            await simple_task.defer_async()

        await async_app.run_worker_async(queues=["default"], wait=False)

    aio_benchmark(defer_and_process_jobs)


@pytest.mark.benchmark
def test_benchmark_1000_async_batch_jobs(aio_benchmark, async_app: app_module.App):
    @async_app.task(queue="default", name="simple_task")
    async def simple_task():
        pass

    async def defer_and_process_jobs():
        await simple_task.batch_defer_async(*[{} for _ in range(1000)])

        await async_app.run_worker_async(queues=["default"], wait=False)

    aio_benchmark(defer_and_process_jobs)
