from __future__ import annotations

import asyncio
import functools
import json

import asgiref.sync
import attr
import pytest

from procrastinate import exceptions, psycopg_connector, sync_psycopg_connector


@pytest.fixture
async def psycopg_connector_factory(psycopg_connection_params):
    connectors = []

    async def _(**kwargs):
        json_dumps = kwargs.pop("json_dumps", None)
        json_loads = kwargs.pop("json_loads", None)
        psycopg_connection_params.update(kwargs)
        connector = psycopg_connector.PsycopgConnector(
            json_dumps=json_dumps, json_loads=json_loads, **psycopg_connection_params
        )
        connectors.append(connector)
        await connector.open_async()
        return connector

    yield _
    for connector in connectors:
        await connector.close_async()


@pytest.mark.parametrize(
    "method_name, expected",
    [
        ("execute_query_one_async", {"json": {"a": "a", "b": "foo"}}),
        ("execute_query_all_async", [{"json": {"a": "a", "b": "foo"}}]),
    ],
)
async def test_execute_query_json_dumps(
    psycopg_connector_factory, mocker, method_name, expected
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
    connector = await psycopg_connector_factory(json_dumps=json_dumps)
    method = getattr(connector, method_name)

    result = await method(query, arg=arg)
    assert result == expected


async def test_json_loads(psycopg_connector_factory, mocker):
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
    connector = await psycopg_connector_factory(json_loads=json_loads)

    result = await connector.execute_query_one_async(query, arg=arg)
    assert result["json"] == {"a": 1, "b": Param(p=2)}


async def test_execute_query(psycopg_connector):
    assert (
        await psycopg_connector.execute_query_async(
            "COMMENT ON TABLE \"procrastinate_jobs\" IS 'foo' "
        )
        is None
    )
    result = await psycopg_connector.execute_query_one_async(
        "SELECT obj_description('public.procrastinate_jobs'::regclass)"
    )
    assert result == {"obj_description": "foo"}

    result = await psycopg_connector.execute_query_all_async(
        "SELECT obj_description('public.procrastinate_jobs'::regclass)"
    )
    assert result == [{"obj_description": "foo"}]


async def test_wrap_exceptions(psycopg_connector):
    await psycopg_connector.execute_query_async(
        """SELECT procrastinate_defer_job(
            'queue', 'foo', 0, NULL, 'lock', '{}', NULL
        ) AS id;"""
    )
    with pytest.raises(exceptions.UniqueViolation):
        await psycopg_connector.execute_query_async(
            """SELECT procrastinate_defer_job(
                'queue', 'foo', 0, NULL, 'lock', '{}', NULL
            ) AS id;"""
        )


async def test_execute_query_sync(psycopg_connector):
    @asgiref.sync.sync_to_async()
    def sync():
        assert (
            psycopg_connector.execute_query(
                "COMMENT ON TABLE \"procrastinate_jobs\" IS 'foo' "
            )
            is None
        )
        result = psycopg_connector.execute_query_one(
            "SELECT obj_description('public.procrastinate_jobs'::regclass)"
        )
        assert result == {"obj_description": "foo"}

        result = psycopg_connector.execute_query_all(
            "SELECT obj_description('public.procrastinate_jobs'::regclass)"
        )
        assert result == [{"obj_description": "foo"}]

    await sync()


async def test_execute_query_interpolate(psycopg_connector):
    result = await psycopg_connector.execute_query_one_async(
        "SELECT %(foo)s as foo;", foo="bar"
    )
    assert result == {"foo": "bar"}


@pytest.mark.filterwarnings("error::ResourceWarning")
async def test_execute_query_simultaneous(psycopg_connector):
    # two coroutines doing execute_query_async simultaneously
    #
    # the test may fail if the connector fails to properly parallelize connections

    async def query():
        await psycopg_connector.execute_query_async("SELECT 1")

    try:
        await asyncio.gather(query(), query())
    except ResourceWarning:
        pytest.fail("ResourceWarning")


async def test_close_async(psycopg_connector):
    await psycopg_connector.execute_query_async("SELECT 1")
    pool = psycopg_connector._async_pool
    await psycopg_connector.close_async()
    assert pool.closed is True
    assert psycopg_connector._async_pool is None


async def test_listen_notify(psycopg_connector):
    channel = "somechannel"
    event = asyncio.Event()

    task = asyncio.ensure_future(
        psycopg_connector.listen_notify(channels=[channel], event=event)
    )
    try:
        await asyncio.wait_for(event.wait(), timeout=0.2)
        event.clear()
        await psycopg_connector.execute_query_async(f"""NOTIFY "{channel}" """)
        await asyncio.wait_for(event.wait(), timeout=1)
    except asyncio.TimeoutError:
        pytest.fail("Notify not received within 1 sec")
    finally:
        task.cancel()


async def test_loop_notify_stop_when_connection_closed(psycopg_connector):
    # We want to make sure that the when the connection is closed, the loop end.
    event = asyncio.Event()
    await psycopg_connector.open_async()
    async with psycopg_connector._async_pool.connection() as connection:
        coro = psycopg_connector._loop_notify(event=event, connection=connection)

    await psycopg_connector._async_pool.close()
    assert connection.closed

    try:
        await asyncio.wait_for(coro, 1)
    except asyncio.TimeoutError:
        pytest.fail("Failed to detect that connection was closed and stop")


async def test_loop_notify_timeout(psycopg_connector):
    # We want to make sure that when the listen starts, we don't listen forever. If the
    # connection closes, we eventually finish the coroutine.
    event = asyncio.Event()
    await psycopg_connector.open_async()
    async with psycopg_connector._async_pool.connection() as connection:
        task = asyncio.ensure_future(
            psycopg_connector._loop_notify(event=event, connection=connection)
        )
        assert not task.done()

    await psycopg_connector._async_pool.close()
    assert connection.closed

    try:
        await asyncio.wait_for(task, 0.1)
    except asyncio.TimeoutError:
        pytest.fail("Failed to detect that connection was closed and stop")

    assert not event.is_set()


async def test_get_sync_connector__open(psycopg_connector):
    assert psycopg_connector.get_sync_connector() is psycopg_connector
    await psycopg_connector.close_async()


async def test_get_sync_connector__not_open(not_opened_psycopg_connector):
    sync = not_opened_psycopg_connector.get_sync_connector()
    assert isinstance(sync, sync_psycopg_connector.SyncPsycopgConnector)
    assert not_opened_psycopg_connector.get_sync_connector() is sync
    assert sync._pool_args == not_opened_psycopg_connector._pool_args
