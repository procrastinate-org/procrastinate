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
        await connector.close_connection()


async def test_get_connection(pg_connector, connection_params):
    async with await pg_connector._get_connection() as connection:

        assert connection.dsn == "dbname=" + connection_params["dbname"]


async def test_get_connection_json_loads(pg_connector_factory, mocker):
    json_loads = mocker.MagicMock()
    register_default_jsonb = mocker.patch("psycopg2.extras.register_default_jsonb")
    connector = pg_connector_factory(json_loads=json_loads)
    async with await connector._get_connection() as connection:
        register_default_jsonb.assert_called_with(connection.raw, loads=json_loads)


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


async def test_close_connection(pg_connector):
    await pg_connector._get_connection()
    await pg_connector.close_connection()
    assert pg_connector._connection.closed == 1


async def test_close_connection_no_connection(pg_connector):
    await pg_connector.close_connection()
    # Well we didn't crash. Great.


async def test_stop_no_connection(pg_connector):
    pg_connector.interrupt_wait()
    # Well we didn't crash. Great.


async def test_get_connection_called_twice(pg_connector):
    conn1 = await pg_connector._get_connection()
    assert not conn1.closed
    conn2 = await pg_connector._get_connection()
    assert conn2 is conn1


async def test_get_connection_after_close(pg_connector):
    conn1 = await pg_connector._get_connection()
    assert not conn1.closed
    await pg_connector.close_connection()
    conn2 = await pg_connector._get_connection()
    assert not conn2.closed
    assert conn2 is not conn1


async def test_get_connection_no_psycopg2_adapter_registration(pg_connector, mocker):
    register_adapter = mocker.patch("psycopg2.extensions.register_adapter")
    await pg_connector._get_connection()
    assert not register_adapter.called
