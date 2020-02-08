import functools
import json

import pytest

from procrastinate import aiopg_connector

pytestmark = pytest.mark.asyncio


async def test_get_connection(connection):
    dsn = connection.dsn
    async with await aiopg_connector.get_connection(dsn=dsn) as new_connection:

        assert new_connection.dsn == dsn


async def test_get_connection_json_loads(connection, mocker):
    dsn = connection.dsn
    json_loads = mocker.MagicMock()
    register_default_jsonb = mocker.patch("psycopg2.extras.register_default_jsonb")
    async with await aiopg_connector.get_connection(
        dsn=dsn, json_loads=json_loads
    ) as new_connection:
        register_default_jsonb.assert_called_with(new_connection.raw, loads=json_loads)


async def test_execute_query_one_json_loads(connection, mocker):
    class NotJSONSerializableByDefault:
        pass

    def encode(obj):
        if isinstance(obj, NotJSONSerializableByDefault):
            return "foo"
        raise TypeError()

    query = "SELECT %(arg)s::jsonb as json"
    arg = {"a": "a", "b": NotJSONSerializableByDefault()}
    json_dumps = functools.partial(json.dumps, default=encode)
    result = await aiopg_connector.execute_query_one(
        connection, query, json_dumps=json_dumps, arg=arg
    )
    assert result["json"] == {"a": "a", "b": "foo"}


async def test_execute_query_all_json_loads(connection, mocker):
    class NotJSONSerializableByDefault:
        pass

    def encode(obj):
        if isinstance(obj, NotJSONSerializableByDefault):
            return "foo"
        raise TypeError()

    query = "SELECT %(arg)s::jsonb as json"
    arg = {"a": "a", "b": NotJSONSerializableByDefault()}
    json_dumps = functools.partial(json.dumps, default=encode)
    result = await aiopg_connector.execute_query_all(
        connection, query, json_dumps=json_dumps, arg=arg
    )
    assert len(result) == 1
    assert result[0]["json"] == {"a": "a", "b": "foo"}


async def test_execute_query(pg_job_store):
    await pg_job_store.execute_query(
        "COMMENT ON TABLE \"procrastinate_jobs\" IS 'foo' "
    )
    result = await pg_job_store.execute_query_one(
        "SELECT obj_description('public.procrastinate_jobs'::regclass)"
    )
    assert result == {"obj_description": "foo"}

    result = await pg_job_store.execute_query_all(
        "SELECT obj_description('public.procrastinate_jobs'::regclass)"
    )
    assert result == [{"obj_description": "foo"}]


async def test_close_connection(pg_job_store):
    await pg_job_store.get_connection()
    await pg_job_store.close_connection()
    assert pg_job_store._connection.closed == 1


async def test_close_connection_no_connection(pg_job_store):
    await pg_job_store.close_connection()
    # Well we didn't crash. Great.


async def test_stop_no_connection(pg_job_store):
    pg_job_store.stop()
    # Well we didn't crash. Great.


async def test_get_connection_called_twice(pg_job_store):
    conn1 = await pg_job_store.get_connection()
    assert not conn1.closed
    conn2 = await pg_job_store.get_connection()
    assert conn2 is conn1


async def test_get_connection_after_close(pg_job_store):
    conn1 = await pg_job_store.get_connection()
    assert not conn1.closed
    await pg_job_store.close_connection()
    conn2 = await pg_job_store.get_connection()
    assert not conn2.closed
    assert conn2 is not conn1


async def test_get_connection_no_psycopg2_adapter_registration(pg_job_store, mocker):
    register_adapter = mocker.patch("psycopg2.extensions.register_adapter")
    await pg_job_store.get_connection()
    assert not register_adapter.called
