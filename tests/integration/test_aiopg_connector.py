import pytest

from procrastinate import aiopg_connector, jobs

pytestmark = pytest.mark.asyncio


async def test_get_connection(connection):
    dsn = connection.get_dsn_parameters()
    async with aiopg_connector.get_connection(**dsn) as new_connection:

        assert new_connection._conn.get_dsn_parameters() == dsn


async def test_defer_job(aiopg_job_store, get_all):
    queue = "marsupilami"
    job = jobs.Job(
        id=0, queue=queue, task_name="bob", lock="sher", task_kwargs={"a": 1, "b": 2}
    )
    pk = await aiopg_job_store.defer_job(job=job)

    result = get_all("procrastinate_jobs", "id", "args", "status", "lock", "task_name")
    assert result == [
        {
            "id": pk,
            "args": {"a": 1, "b": 2},
            "status": "todo",
            "lock": "sher",
            "task_name": "bob",
        }
    ]


async def test_get_sync_store(aiopg_job_store):
    sync_store = aiopg_job_store.get_sync_store()

    async_connection = await aiopg_job_store.get_connection()
    assert (
        sync_store.connection.get_dsn_parameters()
        == async_connection._conn.get_dsn_parameters()
    )
