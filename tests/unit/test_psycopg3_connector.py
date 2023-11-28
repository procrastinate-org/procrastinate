import psycopg
import pytest

from procrastinate import exceptions, psycopg3_connector


@pytest.fixture
def connector():
    return psycopg3_connector.Psycopg3Connector()


async def test_adapt_pool_args_configure(mocker):
    called = []

    async def configure(connection):
        called.append(connection)

    args = psycopg3_connector.Psycopg3Connector._adapt_pool_args(
        pool_args={"configure": configure}, json_loads=None, json_dumps=None
    )

    assert args["configure"] is not configure

    connection = mocker.Mock(_pool=None)
    await args["configure"](connection)

    assert called == [connection]


async def test_wrap_exceptions_wraps():
    @psycopg3_connector.wrap_exceptions
    async def corofunc():
        raise psycopg.DatabaseError

    coro = corofunc()

    with pytest.raises(exceptions.ConnectorException):
        await coro


async def test_wrap_exceptions_success():
    @psycopg3_connector.wrap_exceptions
    async def corofunc(a, b):
        return a, b

    assert await corofunc(1, 2) == (1, 2)


@pytest.mark.parametrize(
    "max_size, expected_calls_count",
    [
        pytest.param(5, 6, id="Valid max_size"),
        pytest.param("5", 1, id="Invalid max_size"),
    ],
)
async def test_wrap_query_exceptions_reached_max_tries(
    mocker, max_size, expected_calls_count
):
    called = []

    @psycopg3_connector.wrap_query_exceptions
    async def corofunc(connector):
        called.append(True)
        raise psycopg.errors.OperationalError(
            "server closed the connection unexpectedly"
        )

    connector = mocker.Mock(_pool=mocker.AsyncMock(max_size=max_size))
    coro = corofunc(connector)

    with pytest.raises(exceptions.ConnectorException) as excinfo:
        await coro

    assert len(called) == expected_calls_count
    assert (
        str(excinfo.value)
        == f"Could not get a valid connection after {expected_calls_count} tries"
    )


@pytest.mark.parametrize(
    "exception_class", [Exception, psycopg.errors.OperationalError]
)
async def test_wrap_query_exceptions_unhandled_exception(mocker, exception_class):
    called = []

    @psycopg3_connector.wrap_query_exceptions
    async def corofunc(connector):
        called.append(True)
        raise exception_class("foo")

    connector = mocker.Mock(_pool=mocker.AsyncMock(max_size=5))
    coro = corofunc(connector)

    with pytest.raises(exception_class):
        await coro

    assert len(called) == 1


async def test_wrap_query_exceptions_success(mocker):
    called = []

    @psycopg3_connector.wrap_query_exceptions
    async def corofunc(connector, a, b):
        if len(called) < 2:
            called.append(True)
            raise psycopg.errors.OperationalError(
                "server closed the connection unexpectedly"
            )
        return a, b

    connector = mocker.Mock(_pool=mocker.AsyncMock(max_size=5))

    assert await corofunc(connector, 1, 2) == (1, 2)
    assert len(called) == 2


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
