import asyncio
import functools
import json

import pytest

from procrastinate import aiopg_connector

pytestmark = pytest.mark.asyncio


@pytest.fixture
async def pg_connector_factory(connection_params):
    connectors = []

    async def _(**kwargs):
        connection_params.update(kwargs)
        connector = await aiopg_connector.PostgresConnector.create_with_pool_async(
            **connection_params
        )
        connectors.append(connector)
        return connector

    yield _
    for connector in connectors:
        await connector.close_async()


async def test_create_with_pool(connection_params):
    connector = await aiopg_connector.PostgresConnector.create_with_pool_async(
        **connection_params
    )
    try:
        async with connector._pool.acquire() as connection:
            assert connection.dsn == "dbname=" + connection_params["dbname"]
    finally:
        await connector.close_async()


@pytest.mark.parametrize(
    "method_name, result",
    [
        ("execute_query_one", {"json": {"a": "a", "b": "foo"}}),
        ("execute_query_all", [{"json": {"a": "a", "b": "foo"}}]),
    ],
)
async def test_execute_query_one_json_loads(
    pg_connector_factory, mocker, method_name, result
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
    connector = await pg_connector_factory(json_dumps=json_dumps)
    method = getattr(connector, method_name)

    result = await method(query, arg=arg)
    assert result == result


async def test_execute_query(pg_connector):
    assert (
        await pg_connector.execute_query(
            "COMMENT ON TABLE \"procrastinate_jobs\" IS 'foo' "
        )
        is None
    )
    result = await pg_connector.execute_query_one(
        "SELECT obj_description('public.procrastinate_jobs'::regclass)"
    )
    assert result == {"obj_description": "foo"}

    result = await pg_connector.execute_query_all(
        "SELECT obj_description('public.procrastinate_jobs'::regclass)"
    )
    assert result == [{"obj_description": "foo"}]


@pytest.mark.filterwarnings("error::ResourceWarning")
async def test_execute_query_simultaneous(pg_connector):
    # two coroutines doing execute_query simulteneously
    #
    # the test may fail if the connector fails to properly parallelize connections

    async def query():
        await pg_connector.execute_query("SELECT 1")

    try:
        await asyncio.gather(query(), query())
    except ResourceWarning:
        pytest.fail("ResourceWarning")


async def test_close_async(pg_connector):
    await pg_connector.execute_query("SELECT 1")
    await pg_connector.close_async()
    assert pg_connector._pool.closed is True


async def test_get_connection_no_psycopg2_adapter_registration(
    connection_params, mocker
):
    register_adapter = mocker.patch("psycopg2.extensions.register_adapter")
    await aiopg_connector.PostgresConnector.create_with_pool_async(**connection_params)
    assert not register_adapter.called


async def test_listen_notify(pg_connector):
    channel = "somechannel"
    event = asyncio.Event()

    task = asyncio.create_task(
        pg_connector.listen_notify(channels=[channel], event=event)
    )
    try:
        await event.wait()
        event.clear()
        await pg_connector.execute_query(f"""NOTIFY "{channel}" """)
        await asyncio.wait_for(event.wait(), timeout=1)
    except asyncio.TimeoutError:
        pytest.fail("Notify not received within 1 sec")
    finally:
        task.cancel()
