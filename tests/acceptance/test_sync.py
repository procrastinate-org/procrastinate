import pytest

import procrastinate

pytestmark = pytest.mark.asyncio


@pytest.fixture
def pg_app(psycopg2_connector):
    return procrastinate.App(connector=psycopg2_connector)


# Even if we test the purely sync parts, we'll still need an async worker to execute
# the tasks
async def test_defer(pg_app, aiopg_connector):

    sum_results = []
    product_results = []

    @pg_app.task(queue="default", name="sum_task")
    def sum_task(a, b):
        sum_results.append(a + b)

    @pg_app.task(queue="default", name="product_task")
    async def product_task(a, b):
        product_results.append(a * b)

    sum_task.defer(a=1, b=2)
    sum_task.configure().defer(a=3, b=4)
    pg_app.configure_task(name="sum_task").defer(a=5, b=6)
    product_task.defer(a=3, b=4)

    async_app = procrastinate.App(connector=aiopg_connector)
    async_app.tasks = pg_app.tasks

    await async_app.run_worker_async(queues=["default"], wait=False)

    assert sum_results == [3, 7, 11]
    assert product_results == [12]
