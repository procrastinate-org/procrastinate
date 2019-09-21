import pytest

import procrastinate

pytestmark = pytest.mark.asyncio


@pytest.fixture
def async_app(aiopg_job_store):
    return procrastinate.App(job_store=aiopg_job_store)


@pytest.fixture
def sync_app(pg_job_store):
    return procrastinate.App(job_store=pg_job_store)


async def test_defer(async_app, sync_app):

    sum_results = []

    @async_app.task(queue="default")
    def sum_task(a, b):
        sum_results.append(a + b)

    # A bit hackish but this way, both apps have the same tasks
    sync_app.tasks = async_app.tasks

    await sum_task.defer_async(a=1, b=2)
    await sum_task.configure().defer_async(a=3, b=4)
    # await async_app.configure_task().defer_async(a=5, b=6)

    # Worker still runs synchrously
    sync_app.run_worker(queues=["default"], only_once=True)

    # assert sum_results == [3, 7, 11]
    assert sum_results == [3, 7]
