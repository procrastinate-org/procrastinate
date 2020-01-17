import pytest
from procrastinate.healthchecks import HealthCheckRunner

pytestmark = pytest.mark.asyncio


async def test_healthchecks(pg_job_store):
    """Running healthchecks should be OK on a clean install."""
    checker = HealthCheckRunner(pg_job_store)

    assert await checker.check_connection_async()
    assert await checker.check_db_version_async()
