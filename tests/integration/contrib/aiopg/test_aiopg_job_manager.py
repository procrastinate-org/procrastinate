from __future__ import annotations

import functools

import pytest

from procrastinate import manager


@pytest.fixture
def pg_job_manager(aiopg_connector):
    return manager.JobManager(connector=aiopg_connector)


@pytest.fixture
def get_all(aiopg_connector):
    async def f(table, *fields):
        return await aiopg_connector.execute_query_all_async(
            f"SELECT {', '.join(fields)} FROM {table}"
        )

    return f


@pytest.fixture
def deferred_job_factory(deferred_job_factory, pg_job_manager):
    return functools.partial(deferred_job_factory, job_manager=pg_job_manager)


async def test_delete_old_jobs_job_todo(
    get_all,
    pg_job_manager,
    psycopg_connector,
    deferred_job_factory,
):
    job = await deferred_job_factory(queue="queue_a")

    # We fake its started event timestamp
    await psycopg_connector.execute_query_async(
        f"UPDATE procrastinate_events SET at=at - INTERVAL '2 hours'"
        f"WHERE job_id={job.id}"
    )

    await pg_job_manager.delete_old_jobs(nb_hours=0)
    assert len(await get_all("procrastinate_jobs", "id")) == 1
