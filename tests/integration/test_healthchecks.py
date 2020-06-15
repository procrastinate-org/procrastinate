import pytest

from procrastinate import jobs
from procrastinate.healthchecks import HealthCheckRunner

pytestmark = pytest.mark.asyncio


@pytest.fixture
def checker(aiopg_connector):
    return HealthCheckRunner(connector=aiopg_connector)


async def test_check_connection(checker):
    assert await checker.check_connection_async() is True


async def test_get_status_count(checker):
    status_count = await checker.get_status_count_async()
    assert set(status_count.keys()) == set(jobs.Status)
    for known_status in jobs.Status:
        assert status_count[known_status] == 0
