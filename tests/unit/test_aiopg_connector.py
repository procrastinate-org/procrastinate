import collections

import psycopg2
import pytest

from procrastinate import aiopg_connector, exceptions


@pytest.fixture
def connector():
    return aiopg_connector.AiopgConnector()


async def test_adapt_pool_args_on_connect(mocker):
    called = []

    async def on_connect(connection):
        called.append(connection)

    args = aiopg_connector.AiopgConnector._adapt_pool_args(
        pool_args={"on_connect": on_connect}, json_loads=None
    )

    assert args["on_connect"] is not on_connect

    connection = mocker.Mock(_pool=None)
    await args["on_connect"](connection)

    assert called == [connection]


async def test_wrap_exceptions_wraps():
    @aiopg_connector.wrap_exceptions
    async def corofunc():
        raise psycopg2.DatabaseError

    coro = corofunc()

    with pytest.raises(exceptions.ConnectorException):
        await coro


async def test_wrap_exceptions_success():
    @aiopg_connector.wrap_exceptions
    async def corofunc(a, b):
        return a, b

    assert await corofunc(1, 2) == (1, 2)


@pytest.mark.parametrize(
    "maxsize, expected_calls_count",
    [
        pytest.param(5, 6, id="Valid maxsize"),
        pytest.param("5", 1, id="Invalid maxsize"),
    ],
)
async def test_wrap_query_exceptions_reached_max_tries(
    mocker, maxsize, expected_calls_count
):
    called = []

    @aiopg_connector.wrap_query_exceptions
    async def corofunc(connector):
        called.append(True)
        raise psycopg2.errors.OperationalError(
            "server closed the connection unexpectedly"
        )

    connector = mocker.Mock(_pool=mocker.Mock(maxsize=maxsize))
    coro = corofunc(connector)

    with pytest.raises(exceptions.ConnectorException) as excinfo:
        await coro

    assert len(called) == expected_calls_count
    assert (
        str(excinfo.value)
        == f"Could not get a valid connection after {expected_calls_count} tries"
    )


@pytest.mark.parametrize(
    "exception_class", [Exception, psycopg2.errors.OperationalError]
)
async def test_wrap_query_exceptions_unhandled_exception(mocker, exception_class):
    called = []

    @aiopg_connector.wrap_query_exceptions
    async def corofunc(connector):
        called.append(True)
        raise exception_class("foo")

    connector = mocker.Mock(_pool=mocker.Mock(maxsize=5))
    coro = corofunc(connector)

    with pytest.raises(exception_class):
        await coro

    assert len(called) == 1


async def test_wrap_query_exceptions_success(mocker):
    called = []

    @aiopg_connector.wrap_query_exceptions
    async def corofunc(connector, a, b):
        if len(called) < 2:
            called.append(True)
            raise psycopg2.errors.OperationalError(
                "server closed the connection unexpectedly"
            )
        return a, b

    connector = mocker.Mock(_pool=mocker.Mock(maxsize=5))

    assert await corofunc(connector, 1, 2) == (1, 2)
    assert len(called) == 2


@pytest.mark.parametrize(
    "method_name",
    [
        "_create_pool",
        "close_async",
        "execute_query_async",
        "_execute_query_connection",
        "execute_query_one_async",
        "execute_query_all_async",
        "listen_notify",
        "_loop_notify",
    ],
)
def test_wrap_exceptions_applied(method_name, connector):
    assert getattr(connector, method_name)._exceptions_wrapped is True


async def test_listen_notify_pool_one_connection(mocker, caplog, connector):
    pool = mocker.Mock(maxsize=1)
    await connector.open_async(pool)
    caplog.clear()

    await connector.listen_notify(None, None)

    assert {e.action for e in caplog.records} == {"listen_notify_disabled"}


# mocker and async don't play very well together (yet), so it's easier to create
# stubs
@pytest.fixture
def fake_connector(mocker):
    class FakePool:
        _free = collections.deque()

        def terminate(self):
            pass

    class FakeConnector(aiopg_connector.AiopgConnector):
        create_pool_called = False
        create_pool_args = None

        async def _create_pool(self, pool_args):
            self.create_pool_called = True
            self.create_pool_args = pool_args
            return FakePool()

    return FakeConnector()


async def test_open_async_no_pool_specified(fake_connector):
    await fake_connector.open_async()

    assert fake_connector._pool_externally_set is False
    assert fake_connector.create_pool_called is True
    assert fake_connector.create_pool_args == fake_connector._pool_args


async def test_open_async_pool_argument_specified(fake_connector):
    pool = object()
    await fake_connector.open_async(pool)

    assert fake_connector._pool_externally_set is True
    assert fake_connector.create_pool_called is False
    assert fake_connector._pool == pool


def test_get_pool(connector):
    with pytest.raises(exceptions.AppNotOpen):
        _ = connector.pool


@pytest.mark.parametrize(
    "query, has_arguments, expected",
    [
        ("a % b", False, "a %% b"),
        ("a % b", True, "a % b"),
        (12, False, 12),
    ],
)
def test_prepare_for_interpolation(query, has_arguments, expected, connector):
    result = connector._prepare_for_interpolation(
        query=query, has_arguments=has_arguments
    )
    assert result == expected
