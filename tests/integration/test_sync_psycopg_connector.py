from __future__ import annotations

import functools
import json

import pytest

from procrastinate import sync_psycopg_connector


@pytest.fixture
def sync_psycopg_connector_factory(psycopg_connection_params):
    connectors = []

    def _(**kwargs):
        json_dumps = kwargs.pop("json_dumps", None)
        json_loads = kwargs.pop("json_loads", None)
        psycopg_connection_params.update(kwargs)
        connector = sync_psycopg_connector.SyncPsycopgConnector(
            json_dumps=json_dumps, json_loads=json_loads, **psycopg_connection_params
        )
        connectors.append(connector)
        connector.open()
        return connector

    yield _
    for connector in connectors:
        connector.close()


@pytest.mark.parametrize(
    "method_name, expected",
    [
        ("execute_query_one", {"json": {"a": "a", "b": "foo"}}),
        ("execute_query_all", [{"json": {"a": "a", "b": "foo"}}]),
    ],
)
def test_execute_query_json_dumps(
    sync_psycopg_connector_factory, mocker, method_name, expected
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
    connector = sync_psycopg_connector_factory(json_dumps=json_dumps)
    method = getattr(connector, method_name)

    result = method(query, arg=arg)
    assert result == expected


def test_json_loads(sync_psycopg_connector_factory, mocker):
    # sync json_loads is only used for CLI defer.
    loads = mocker.Mock()
    connector = sync_psycopg_connector_factory(json_loads=loads)
    assert connector._json_loads is loads


def test_execute_query(sync_psycopg_connector):
    sync_psycopg_connector.execute_query(
        "COMMENT ON TABLE \"procrastinate_jobs\" IS 'foo'"
    )
    result = sync_psycopg_connector.execute_query_one(
        "SELECT obj_description('public.procrastinate_jobs'::regclass)"
    )
    assert result == {"obj_description": "foo"}

    result = sync_psycopg_connector.execute_query_all(
        "SELECT obj_description('public.procrastinate_jobs'::regclass)"
    )
    assert result == [{"obj_description": "foo"}]


def test_execute_query_arg(sync_psycopg_connector):
    sync_psycopg_connector.execute_query("SELECT %(arg)s", arg=1)
    result = sync_psycopg_connector.execute_query_one("SELECT %(arg)s", arg=1)
    assert result == {"?column?": 1}

    result = sync_psycopg_connector.execute_query_all("SELECT %(arg)s", arg=1)
    assert result == [{"?column?": 1}]


def test_close(sync_psycopg_connector):
    pool = sync_psycopg_connector._pool
    sync_psycopg_connector.close()
    assert pool.closed is True
