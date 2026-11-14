from __future__ import annotations

import asyncio
import contextlib

import psycopg
import pytest

from procrastinate import exceptions, psycopg_connector

from ..helpers import wait_or_fail


@pytest.fixture
def connector():
    return psycopg_connector.PsycopgConnector()


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


class CancellationSwallowingConnection:
    """Swallows the first cancellation of its notifications, as some drivers do."""

    def __init__(self, on_cancel: type[BaseException] | None = None):
        self.listening = asyncio.Event()
        self.on_cancel = on_cancel
        self.swallowed = False

    async def notifies(self):
        self.listening.set()
        try:
            await asyncio.Event().wait()
        except asyncio.CancelledError:
            if self.swallowed:
                raise
            self.swallowed = True
            if self.on_cancel:
                raise self.on_cancel from None
            return
        yield  # pragma: no cover

    async def execute(self, *args, **kwargs):
        pass


async def handle_notification(channel: str, payload: str):
    pass


async def test_loop_notify_cancelled_despite_swallowed_cancellation(connector):
    connection = CancellationSwallowingConnection()
    task = asyncio.create_task(
        connector._loop_notify(
            on_notification=handle_notification, connection=connection
        )
    )
    await wait_or_fail(connection.listening.wait())

    task.cancel()

    with pytest.raises(asyncio.CancelledError):
        await wait_or_fail(task)


async def test_listen_notify_cancelled_despite_swallowed_cancellation(
    connector, mocker
):
    connection = CancellationSwallowingConnection(on_cancel=psycopg.OperationalError)

    @contextlib.asynccontextmanager
    async def get_standalone_connection():
        yield connection

    mocker.patch.object(
        connector, "_get_standalone_connection", get_standalone_connection
    )
    task = asyncio.create_task(
        connector.listen_notify(on_notification=handle_notification, channels=["a"])
    )
    await wait_or_fail(connection.listening.wait())

    task.cancel()

    with pytest.raises(asyncio.CancelledError):
        await wait_or_fail(task)
