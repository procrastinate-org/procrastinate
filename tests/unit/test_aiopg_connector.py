import psycopg2
import pytest

from procrastinate import aiopg_connector, exceptions


@pytest.mark.asyncio
async def test_adapt_pool_args_on_connect(mocker):
    called = []

    async def on_connect(connection):
        called.append(connection)

    args = aiopg_connector.PostgresConnector._adapt_pool_args(
        pool_args={"on_connect": on_connect}, json_loads=None
    )

    assert args["on_connect"] is not on_connect

    connection = mocker.Mock()
    await args["on_connect"](connection)

    assert called == [connection]


def test_adapt_pool_args_maxsize():
    args = aiopg_connector.PostgresConnector._adapt_pool_args(
        pool_args={"maxsize": 1}, json_loads=None
    )

    assert args["maxsize"] == 2


@pytest.mark.parametrize(
    "psycopg2_exception, procrastinate_exception",
    [
        (psycopg2.DatabaseError, exceptions.ConnectorException),
        (psycopg2.errors.ExclusionViolation, exceptions.DeferLockTaken),
    ],
)
@pytest.mark.asyncio
async def test_wrap_exceptions_wraps(psycopg2_exception, procrastinate_exception):
    @aiopg_connector.wrap_exceptions
    async def corofunc():
        raise psycopg2_exception

    coro = corofunc()

    with pytest.raises(procrastinate_exception):
        await coro


@pytest.mark.asyncio
async def test_wrap_exceptions_success():
    @aiopg_connector.wrap_exceptions
    async def corofunc(a, b):
        return a, b

    assert await corofunc(1, 2) == (1, 2)


@pytest.mark.parametrize(
    "method_name",
    [
        "close_async",
        "_create_pool",
        "execute_query",
        "_execute_query_connection",
        "execute_query_one",
        "execute_query_all",
        "listen_notify",
        "_loop_notify",
    ],
)
def test_wrap_exceptions_applied(method_name):
    connector = aiopg_connector.PostgresConnector()
    assert getattr(connector, method_name)._exceptions_wrapped is True


def test_set_pool(mocker):
    pool = mocker.Mock()
    connector = aiopg_connector.PostgresConnector()

    connector.set_pool(pool)

    assert connector._pool is pool


def test_set_pool_already_set(mocker):
    pool = mocker.Mock()
    connector = aiopg_connector.PostgresConnector()
    connector.set_pool(pool)

    with pytest.raises(exceptions.PoolAlreadySet):
        connector.set_pool(pool)
