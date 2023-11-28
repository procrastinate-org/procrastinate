import asyncio
import functools
import json

import attr
import pytest

from procrastinate import psycopg3_connector


@pytest.fixture
async def psycopg3_connector_factory(psycopg3_connection_params):
    connectors = []

    async def _(**kwargs):
        json_dumps = kwargs.pop("json_dumps", None)
        json_loads = kwargs.pop("json_loads", None)
        psycopg3_connection_params.update(kwargs)
        connector = psycopg3_connector.Psycopg3Connector(
            json_dumps=json_dumps, json_loads=json_loads, **psycopg3_connection_params
        )
        connectors.append(connector)
        await connector.open_async()
        return connector

    yield _
    for connector in connectors:
        await connector.close_async()


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


@pytest.mark.parametrize(
    "method_name, expected",
    [
        ("execute_query_one_async", {"json": {"a": "a", "b": "foo"}}),
        ("execute_query_all_async", [{"json": {"a": "a", "b": "foo"}}]),
    ],
)
async def test_execute_query_json_dumps(
    psycopg3_connector_factory, mocker, method_name, expected
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
    connector = await psycopg3_connector_factory(json_dumps=json_dumps)
    method = getattr(connector, method_name)

    result = await method(query, arg=arg)
    assert result == expected


async def test_json_loads(psycopg3_connector_factory, mocker):
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
    connector = await psycopg3_connector_factory(json_loads=json_loads)

    result = await connector.execute_query_one_async(query, arg=arg)
    assert result["json"] == {"a": 1, "b": Param(p=2)}


async def test_execute_query(psycopg3_connector):
    assert (
        await psycopg3_connector.execute_query_async(
            "COMMENT ON TABLE \"procrastinate_jobs\" IS 'foo' "
        )
        is None
    )
    result = await psycopg3_connector.execute_query_one_async(
        "SELECT obj_description('public.procrastinate_jobs'::regclass)"
    )
    assert result == {"obj_description": "foo"}

    result = await psycopg3_connector.execute_query_all_async(
        "SELECT obj_description('public.procrastinate_jobs'::regclass)"
    )
    assert result == [{"obj_description": "foo"}]


async def test_execute_query_interpolate(psycopg3_connector):
    result = await psycopg3_connector.execute_query_one_async(
        "SELECT %(foo)s as foo;", foo="bar"
    )
    assert result == {"foo": "bar"}


@pytest.mark.filterwarnings("error::ResourceWarning")
async def test_execute_query_simultaneous(psycopg3_connector):
    # two coroutines doing execute_query_async simultaneously
    #
    # the test may fail if the connector fails to properly parallelize connections

    async def query():
        await psycopg3_connector.execute_query_async("SELECT 1")

    try:
        await asyncio.gather(query(), query())
    except ResourceWarning:
        pytest.fail("ResourceWarning")


async def test_close_async(psycopg3_connector):
    await psycopg3_connector.execute_query_async("SELECT 1")
    pool = psycopg3_connector._pool
    await psycopg3_connector.close_async()
    assert pool.closed is True
    assert psycopg3_connector._pool is None


async def test_listen_notify(psycopg3_connector):
    channel = "somechannel"
    event = asyncio.Event()

    task = asyncio.ensure_future(
        psycopg3_connector.listen_notify(channels=[channel], event=event)
    )
    try:
        await event.wait()
        event.clear()
        await psycopg3_connector.execute_query_async(f"""NOTIFY "{channel}" """)
        await asyncio.wait_for(event.wait(), timeout=1)
    except asyncio.TimeoutError:
        pytest.fail("Notify not received within 1 sec")
    finally:
        task.cancel()


async def test_loop_notify_stop_when_connection_closed(psycopg3_connector):
    # We want to make sure that the when the connection is closed, the loop end.
    event = asyncio.Event()
    await psycopg3_connector.open_async()
    async with psycopg3_connector._pool.connection() as connection:
        coro = psycopg3_connector._loop_notify(event=event, connection=connection)

    await psycopg3_connector._pool.close()
    assert connection.closed

    try:
        await asyncio.wait_for(coro, 1)
    except asyncio.TimeoutError:
        pytest.fail("Failed to detect that connection was closed and stop")


async def test_loop_notify_timeout(psycopg3_connector):
    # We want to make sure that when the listen starts, we don't listen forever. If the
    # connection closes, we eventually finish the coroutine.
    event = asyncio.Event()
    await psycopg3_connector.open_async()
    async with psycopg3_connector._pool.connection() as connection:
        task = asyncio.ensure_future(
            psycopg3_connector._loop_notify(event=event, connection=connection)
        )
        assert not task.done()

    await psycopg3_connector._pool.close()
    assert connection.closed

    try:
        await asyncio.wait_for(task, 0.1)
    except asyncio.TimeoutError:
        pytest.fail("Failed to detect that connection was closed and stop")

    assert not event.is_set()


async def test_destructor():
    ...
