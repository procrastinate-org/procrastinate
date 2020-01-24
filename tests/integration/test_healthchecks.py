import pytest
from procrastinate import jobs
from procrastinate.healthchecks import HealthCheckRunner

pytestmark = pytest.mark.asyncio


async def test_healthchecks(pg_job_store):
    """Running healthchecks should be OK on a clean install."""
    checker = HealthCheckRunner(pg_job_store)

    assert await checker.check_connection_async()
    assert await checker.check_db_version_async()

    status_count = await checker.get_status_count_async()
    assert set(status_count.keys()) == set(jobs.Status)
    for known_status in jobs.Status:
        assert status_count[known_status] == 0
