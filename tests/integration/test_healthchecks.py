import psycopg2
import pytest

from procrastinate import aiopg_connector, jobs
from procrastinate.healthchecks import HealthCheckRunner
from procrastinate.migration import Migrator

pytestmark = pytest.mark.asyncio


@pytest.fixture
def checker(pg_connector):
    return HealthCheckRunner(connector=pg_connector)


async def test_check_connection(checker):
    assert await checker.check_connection_async() is True


async def test_get_schema_version(checker):
    assert await checker.get_schema_version_async() == Migrator.version


async def test_get_status_count(checker):
    status_count = await checker.get_status_count_async()
    assert set(status_count.keys()) == set(jobs.Status)
    for known_status in jobs.Status:
        assert status_count[known_status] == 0


@pytest.mark.parametrize(
    "method",
    ["check_connection_async", "get_schema_version_async", "get_status_count_async"],
)
async def test_db_down(method):
    bad_job_store = aiopg_connector.PostgresConnector(dsn="", dbname="a_bad_db_name")
    checker = HealthCheckRunner(bad_job_store)

    with pytest.raises(psycopg2.Error):
        await getattr(checker, method)()
