import psycopg
import pytest

from procrastinate import exceptions, psycopg_connector


@pytest.fixture
def connector():
    return psycopg_connector.PsycopgConnector()


async def test_adapt_pool_args_configure(mocker):
    called = []

    async def configure(connection):
        called.append(connection)

    args = psycopg_connector.PsycopgConnector._adapt_pool_args(
        pool_args={"configure": configure}, json_loads=None, json_dumps=None
    )

    assert args["configure"] is not configure

    connection = mocker.Mock(_pool=None)
    await args["configure"](connection)

    assert called == [connection]


async def test_wrap_exceptions_wraps():
    @psycopg_connector.wrap_exceptions
    async def corofunc():
        raise psycopg.DatabaseError

    coro = corofunc()

    with pytest.raises(exceptions.ConnectorException):
        await coro


async def test_wrap_exceptions_success():
    @psycopg_connector.wrap_exceptions
    async def corofunc(a, b):
        return a, b

    assert await corofunc(1, 2) == (1, 2)


@pytest.mark.parametrize(
    "method_name",
    [
        "_create_pool",
        "close_async",
        "execute_query_async",
        "execute_query_one_async",
        "execute_query_all_async",
        "listen_notify",
    ],
)
def test_wrap_exceptions_applied(method_name, connector):
    assert getattr(connector, method_name)._exceptions_wrapped is True


async def test_listen_notify_pool_one_connection(mocker, caplog, connector):
    pool = mocker.AsyncMock(max_size=1)
    await connector.open_async(pool)
    caplog.clear()

    await connector.listen_notify(None, None)

    assert {e.action for e in caplog.records} == {"listen_notify_disabled"}


async def test_open_async_no_pool_specified(mocker, connector):
    mocker.patch.object(connector, "_create_pool", return_value=mocker.AsyncMock())

    await connector.open_async()

    assert connector._create_pool.call_count == 1
    assert connector._pool.open.await_count == 1


async def test_open_async_pool_argument_specified(mocker, connector):
    mocker.patch.object(connector, "_create_pool")
    pool = mocker.AsyncMock()

    await connector.open_async(pool)

    assert connector._pool_externally_set is True
    assert connector._create_pool.call_count == 0
    assert connector._pool == pool


def test_get_pool(connector):
    with pytest.raises(exceptions.AppNotOpen):
        _ = connector.pool
