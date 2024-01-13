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


# Even if we test the purely sync parts, we'll still need an async worker to execute
# the tasks
async def test_defer(sync_app, async_app):
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
