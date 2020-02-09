import functools
import json

import pytest

from procrastinate import aiopg_connector

pytestmark = pytest.mark.asyncio


@pytest.fixture
async def pg_connector_factory(connection_params):
    connectors = []

    def _(**kwargs):
        connection_params.update(kwargs)
        connector = aiopg_connector.PostgresConnector(**connection_params)
        connectors.append(connector)
        return connector

    yield _
    for connector in connectors:
        await connector.close_pool()


async def test_get_pool(pg_connector, connection_params):
    async with await pg_connector._get_pool() as pool:
        async with pool.acquire() as conn:
            assert conn.dsn == "dbname=" + connection_params["dbname"]


async def test_get_pool_json_loads(pg_connector_factory, mocker):
    json_loads = mocker.MagicMock()
    register_default_jsonb = mocker.patch("psycopg2.extras.register_default_jsonb")
    connector = pg_connector_factory(json_loads=json_loads)
    async with await connector._get_pool() as pool:
        async with pool.acquire() as conn:
            register_default_jsonb.assert_called_with(conn.raw, loads=json_loads)


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
    connector = pg_connector_factory(json_dumps=json_dumps)
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


async def test_close_pool(pg_connector):
    await pg_connector._get_pool()
    await pg_connector.close_pool()
    assert pg_connector._pool.closed == 1


async def test_close_pool_no_pool(pg_connector):
    await pg_connector.close_pool()
    # Well we didn't crash. Great.


async def test_stop_no_pool(pg_connector):
    pg_connector.interrupt_wait()
    # Well we didn't crash. Great.


async def test_get_pool_called_twice(pg_connector):
    pool1 = await pg_connector._get_pool()
    assert not pool1.closed
    pool2 = await pg_connector._get_pool()
    assert pool2 is pool1


async def test_get_pool_after_close(pg_connector):
    pool1 = await pg_connector._get_pool()
    assert not pool1.closed
    await pg_connector.close_pool()
    pool2 = await pg_connector._get_pool()
    assert not pool2.closed
    assert pool2 is not pool1


async def test_get_pool_no_psycopg2_adapter_registration(pg_connector, mocker):
    register_adapter = mocker.patch("psycopg2.extensions.register_adapter")
    await pg_connector._get_pool()
    assert not register_adapter.called
