from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager

import psycopg
import pytest

from procrastinate import exceptions, psycopg_connector


@pytest.fixture
def connector():
    return psycopg_connector.PsycopgConnector(listen_notify_reconnect_interval=0.0)


async def test_wrap_exceptions_wraps():
    @psycopg_connector.wrap_exceptions()
    async def corofunc():
        raise psycopg.DatabaseError

    coro = corofunc()

    with pytest.raises(exceptions.ConnectorException):
        await coro


async def test_wrap_exceptions_success():
    @psycopg_connector.wrap_exceptions()
    async def corofunc(a, b):
        return a, b

    assert await corofunc(1, 2) == (1, 2)


def test_init_default_listen_notify_reconnect_interval():
    connector = psycopg_connector.PsycopgConnector()
    assert connector._listen_notify_reconnect_interval == 2.0


def test_init_custom_listen_notify_reconnect_interval():
    connector = psycopg_connector.PsycopgConnector(listen_notify_reconnect_interval=5.0)
    assert connector._listen_notify_reconnect_interval == 5.0


@pytest.mark.parametrize(
    "connector, expected_sleep_duration",
    [
        (psycopg_connector.PsycopgConnector(listen_notify_reconnect_interval=1.5), 1.5),
        (psycopg_connector.PsycopgConnector(), 2.0),
    ],
)
async def test_listen_notify_reconnect_interval(
    mocker, connector, expected_sleep_duration
):
    mock_connection = mocker.AsyncMock()
    mock_connection.execute.side_effect = psycopg.OperationalError("Connection lost")

    @asynccontextmanager
    async def mock_get_connection():
        yield mock_connection

    mocker.patch.object(
        connector, "_get_standalone_connection", side_effect=mock_get_connection
    )

    sleep_call_count = 0

    async def mock_sleep(duration):
        nonlocal sleep_call_count
        sleep_call_count += 1
        if sleep_call_count >= 2:
            raise asyncio.CancelledError("Stop the loop")
        assert duration == expected_sleep_duration

    mocker.patch("asyncio.sleep", side_effect=mock_sleep)
    mocker.patch.object(connector, "_loop_notify")

    with pytest.raises(asyncio.CancelledError):
        await connector.listen_notify(mocker.AsyncMock(), ["test_channel"])

    assert sleep_call_count >= 1


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
    assert hasattr(getattr(connector, method_name), "__wrapped__")


async def test_open_async_no_pool_specified(mocker, connector):
    mocker.patch.object(connector, "_create_pool", return_value=mocker.AsyncMock())

    await connector.open_async()

    assert connector._create_pool.call_count == 1
    assert connector._async_pool.open.await_count == 1


async def test_open_async_pool_argument_specified(mocker, connector):
    mocker.patch.object(connector, "_create_pool")
    pool = mocker.AsyncMock()

    await connector.open_async(pool)

    assert connector._pool_externally_set is True
    assert connector._create_pool.call_count == 0
    assert connector._async_pool == pool


async def test_open_async_pool_factory(mocker):
    pool = mocker.AsyncMock()

    def pool_factory(**kwargs):
        return pool

    connector = psycopg_connector.PsycopgConnector(pool_factory=pool_factory)

    await connector.open_async()

    assert connector._async_pool is pool
    assert connector._async_pool.open.await_count == 1


async def test_open_async_pool_factory_argument_specified(mocker):
    pool = mocker.AsyncMock()

    def pool_factory(**kwargs):
        return pool

    connector = psycopg_connector.PsycopgConnector(pool_factory=pool_factory)
    mocker.patch.object(connector, "_create_pool")
    another_pool = mocker.AsyncMock()

    await connector.open_async(another_pool)

    assert connector._pool_externally_set is True
    assert connector._create_pool.call_count == 0
    assert connector._async_pool is another_pool


def test_get_pool(connector):
    with pytest.raises(exceptions.AppNotOpen):
        _ = connector.pool
