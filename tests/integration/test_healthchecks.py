import pytest

from procrastinate import aiopg_connector, jobs
from procrastinate.healthchecks import HealthCheckRunner

pytestmark = pytest.mark.asyncio


async def test_healthchecks(pg_job_store):
    """Running healthchecks should be OK on a clean install."""
    checker = HealthCheckRunner(pg_job_store)

    assert await checker.check_connection_async() == (True, "OK")
    assert await checker.check_db_version_async() == (True, "OK")

    status_count = await checker.get_status_count_async()
    assert set(status_count.keys()) == set(jobs.Status)
    for known_status in jobs.Status:
        assert status_count[known_status] == 0


async def test_db_down():
    bad_job_store = aiopg_connector.PostgresJobStore(dsn="", dbname="a_bad_db_name")
    checker = HealthCheckRunner(bad_job_store)

    check_conn = await checker.check_connection_async()
    check_version = await checker.check_db_version_async()
    assert not check_conn[0]
    assert not check_version[0]
