import pytest

import procrastinate

pytestmark = pytest.mark.asyncio


@pytest.fixture
def sync_app_explicit_open(not_opened_psycopg2_connector):
    app = procrastinate.App(connector=not_opened_psycopg2_connector).open()
    yield app
    app.close()


@pytest.fixture
def sync_app_context_manager(not_opened_psycopg2_connector):
    with procrastinate.App(connector=not_opened_psycopg2_connector).open() as app:
        yield app


@pytest.fixture(
    params=[
        pytest.param(False, id="explicit open"),
        pytest.param(True, id="context manager open"),
    ]
)
async def sync_app(request, sync_app_explicit_open, sync_app_context_manager):
    if request.param:
        yield sync_app_explicit_open
    else:
        yield sync_app_context_manager


# Even if we test the purely sync parts, we'll still need an async worker to execute
# the tasks
async def test_defer(sync_app, async_app_explicit_open):

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

    async_app_explicit_open.tasks = sync_app.tasks
    await async_app_explicit_open.run_worker_async(queues=["default"], wait=False)

    assert sum_results == [3, 7, 11]
    assert product_results == [12]
