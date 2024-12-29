from __future__ import annotations

import asyncio
import functools
import json

import attr
import pytest

from procrastinate.contrib.aiopg import aiopg_connector as aiopg
from procrastinate.contrib.psycopg2 import psycopg2_connector


async def test_adapt_pool_args_on_connect(mocker):
    called = []

    async def on_connect(connection):
        called.append(connection)

    args = aiopg.AiopgConnector._adapt_pool_args(
        pool_args={"on_connect": on_connect}, json_loads=None
    )

    assert args["on_connect"] is not on_connect

    connection = mocker.Mock(_pool=None)
    await args["on_connect"](connection)

    assert called == [connection]


@pytest.mark.parametrize(
    "method_name, expected",
    [
        ("execute_query_one_async", {"json": {"a": "a", "b": "foo"}}),
        ("execute_query_all_async", [{"json": {"a": "a", "b": "foo"}}]),
    ],
)
async def test_execute_query_json_dumps(
    aiopg_connector_factory, mocker, method_name, expected
):
    class NotJSONSerializableByDefault:
        pass

    def encode(obj):
        if isinstance(obj, NotJSONSerializableByDefault):
            return "foo"
        raise TypeError()

    query = "SELECT %(arg)s::jsonb as json"
    arg = {"a": "a", "b": NotJSONSerializableByDefault()}
    json_dumps = functools.partial(json.dumps, default=encode)
    connector = await aiopg_connector_factory(json_dumps=json_dumps)
    method = getattr(connector, method_name)

    result = await method(query, arg=arg)
    assert result == expected


async def test_json_loads(aiopg_connector_factory, mocker):
    @attr.dataclass
    class Param:
        p: int

    def decode(dct):
        if "b" in dct:
            dct["b"] = Param(p=dct["b"])
        return dct

    json_loads = functools.partial(json.loads, object_hook=decode)

    query = "SELECT %(arg)s::jsonb as json"
    arg = {"a": 1, "b": 2}
    connector = await aiopg_connector_factory(json_loads=json_loads)

    result = await connector.execute_query_one_async(query, arg=arg)
    assert result["json"] == {"a": 1, "b": Param(p=2)}


async def test_execute_query(aiopg_connector):
    assert (
        await aiopg_connector.execute_query_async(
            "COMMENT ON TABLE \"procrastinate_jobs\" IS 'foo' "
        )
        is None
    )
    result = await aiopg_connector.execute_query_one_async(
        "SELECT obj_description('public.procrastinate_jobs'::regclass)"
    )
    assert result == {"obj_description": "foo"}

    result = await aiopg_connector.execute_query_all_async(
        "SELECT obj_description('public.procrastinate_jobs'::regclass)"
    )
    assert result == [{"obj_description": "foo"}]


async def test_get_sync_connector(aiopg_connector_factory):
    result = []

    aiopg_connector = await aiopg_connector_factory(open=False)

    def f():
        sync_conn = aiopg_connector.get_sync_connector()
        sync_conn.open()
        try:
            result.append(sync_conn.execute_query_one("SELECT 1"))
        finally:
            sync_conn.close()

    await asyncio.to_thread(f)
    assert list(result[0].values()) == [1]


async def test_execute_query_interpolate(aiopg_connector):
    result = await aiopg_connector.execute_query_one_async(
        "SELECT %(foo)s as foo;", foo="bar"
    )
    assert result == {"foo": "bar"}


@pytest.mark.filterwarnings("error::ResourceWarning")
async def test_execute_query_simultaneous(aiopg_connector):
    # two coroutines doing execute_query_async simulteneously
    #
    # the test may fail if the connector fails to properly parallelize connections

    async def query():
        await aiopg_connector.execute_query_async("SELECT 1")

    try:
        await asyncio.gather(query(), query())
    except ResourceWarning:
        pytest.fail("ResourceWarning")


async def test_close_async(aiopg_connector):
    await aiopg_connector.execute_query_async("SELECT 1")
    pool = aiopg_connector._pool
    await aiopg_connector.close_async()
    assert pool.closed is True
    assert aiopg_connector._pool is None


async def test_get_connection_no_psycopg2_adapter_registration(
    aiopg_connector_factory, mocker
):
    register_adapter = mocker.patch("psycopg2.extensions.register_adapter")
    connector = await aiopg_connector_factory()
    await connector.open_async()
    assert not register_adapter.called


async def test_listen_notify(aiopg_connector):
    channel = "somechannel"
    event = asyncio.Event()
    received_args: list[dict] = []

    async def handle_notification(*, channel: str, payload: str):
        event.set()
        received_args.append({"channel": channel, "payload": payload})

    task = asyncio.ensure_future(
        aiopg_connector.listen_notify(
            channels=[channel], on_notification=handle_notification
        )
    )
    try:
        await asyncio.sleep(0.1)
        await aiopg_connector.execute_query_async(
            f"""NOTIFY "{channel}", 'somepayload' """
        )
        await asyncio.wait_for(event.wait(), timeout=1)
        args = received_args.pop()
        assert args["channel"] == "somechannel"
        assert args["payload"] == "somepayload"
    except asyncio.TimeoutError:
        pytest.fail("Notify not received within 1 sec")
    finally:
        task.cancel()


async def test_loop_notify_stop_when_connection_closed_old_aiopg(aiopg_connector):
    # We want to make sure that the when the connection is closed, the loop end.
    event = asyncio.Event()

    async def handle_notification(channel: str, payload: str):
        event.set()

    await aiopg_connector.open_async()
    async with aiopg_connector._pool.acquire() as connection:
        coro = aiopg_connector._loop_notify(
            on_notification=handle_notification, connection=connection
        )
        await asyncio.sleep(0.1)
        # Currently, the the connection closes, the notifies queue is not
        # awaken. This test validates the "normal" stopping condition, there is
        # a separate test for the timeout.
        connection.close()
        await connection.notifies._queue.put("s")
        try:
            await asyncio.wait_for(coro, 0.1)
        except asyncio.TimeoutError:
            pytest.fail("Failed to detect that connection was closed and stop")


async def test_loop_notify_stop_when_connection_closed(aiopg_connector):
    # We want to make sure that the when the connection is closed, the loop end.
    event = asyncio.Event()

    async def handle_notification(channel: str, payload: str):
        event.set()

    await aiopg_connector.open_async()
    async with aiopg_connector._pool.acquire() as connection:
        coro = aiopg_connector._loop_notify(
            on_notification=handle_notification, connection=connection
        )
        await asyncio.sleep(0.1)
        # Currently, the the connection closes, the notifies queue is not
        # awaken. This test validates the "normal" stopping condition, there is
        # a separate test for the timeout.
        connection.close()
        connection.notifies.close(exception=Exception())
        try:
            await asyncio.wait_for(coro, 0.1)
        except asyncio.TimeoutError:
            pytest.fail("Failed to detect that connection was closed and stop")


async def test_loop_notify_timeout(aiopg_connector):
    # We want to make sure that when the listen starts, we don't listen forever. If the
    # connection closes, we eventually finish the coroutine.
    event = asyncio.Event()

    async def handle_notification(channel: str, payload: str):
        event.set()

    await aiopg_connector.open_async()
    async with aiopg_connector._pool.acquire() as connection:
        task = asyncio.ensure_future(
            aiopg_connector._loop_notify(
                on_notification=handle_notification, connection=connection, timeout=0.01
            )
        )
        await asyncio.sleep(0.1)
        assert not task.done()
        connection.close()
        try:
            await asyncio.wait_for(task, 0.1)
        except asyncio.TimeoutError:
            pytest.fail("Failed to detect that connection was closed and stop")

    assert not event.is_set()


async def test_destructor(connection_params, capsys):
    connector = aiopg.AiopgConnector(**connection_params)
    await connector.open_async()
    await connector.execute_query_async("SELECT 1")

    assert connector._pool
    assert len(connector._pool._free) == 1

    # "del connector" causes a ResourceWarning from aiopg.Pool if the
    # AiopgConnector destructor doesn't close the connections managed
    # by the pool. Unfortunately there's no way to catch that warning,
    # even by using filterwarnings to turn it into an exception, as
    # Python ignores exceptions that occur in destructors
    del connector


async def test_get_sync_connector__open(aiopg_connector):
    await aiopg_connector.open_async()
    assert aiopg_connector.get_sync_connector() is aiopg_connector
    await aiopg_connector.close_async()


async def test_get_sync_connector__not_open(connection_params):
    aiopg_connector = aiopg.AiopgConnector(**connection_params)
    sync = aiopg_connector.get_sync_connector()
    assert isinstance(sync, psycopg2_connector.Psycopg2Connector)
    assert aiopg_connector.get_sync_connector() is sync
