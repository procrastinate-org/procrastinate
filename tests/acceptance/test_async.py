import pytest

import procrastinate

pytestmark = pytest.mark.asyncio


@pytest.fixture
def pg_app(pg_connector):
    return procrastinate.App(connector=pg_connector)


async def test_defer(pg_app):

    sum_results = []
    product_results = []

    @pg_app.task(queue="default", name="sum_task")
    def sum_task(a, b):
        sum_results.append(a + b)

    @pg_app.task(queue="default", name="product_task")
    async def product_task(a, b):
        product_results.append(a * b)

    await sum_task.defer_async(a=1, b=2)
    await sum_task.configure().defer_async(a=3, b=4)
    await pg_app.configure_task(name="sum_task").defer_async(a=5, b=6)
    await product_task.defer_async(a=3, b=4)

    await pg_app.run_worker_async(queues=["default"], wait=False)

    assert sum_results == [3, 7, 11]
    assert product_results == [12]
