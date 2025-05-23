from __future__ import annotations

import functools
import json

import psycopg2.errors
import pytest

from procrastinate import exceptions, manager
from procrastinate.contrib import psycopg2 as proc_psycopg2


@pytest.fixture
def psycopg2_connector_factory(connection_params):
    connectors = []

    def _(**kwargs):
        json_dumps = kwargs.pop("json_dumps", None)
        json_loads = kwargs.pop("json_loads", None)
        connection_params.update(kwargs)
        connector = proc_psycopg2.Psycopg2Connector(
            json_dumps=json_dumps, json_loads=json_loads, **connection_params
        )
        connectors.append(connector)
        connector.open()
        return connector

    yield _
    for connector in connectors:
        connector.close()


@pytest.fixture
def psycopg2_connector(psycopg2_connector_factory):
    return psycopg2_connector_factory()


def test_connection(psycopg2_connector_factory, connection_params):
    connector = psycopg2_connector_factory()
    with connector._connection() as connection:
        assert connection.dsn == "dbname=" + connection_params["dbname"]


@pytest.mark.parametrize("exception", [Exception, psycopg2.errors.AdminShutdown])
def test_connection_exception(psycopg2_connector_factory, connection_params, exception):
    connector = psycopg2_connector_factory()
    with pytest.raises(exception):
        with connector._connection():
            raise exception


@pytest.mark.parametrize(
    "method_name, expected",
    [
        ("execute_query_one", {"json": {"a": "a", "b": "foo"}}),
        ("execute_query_all", [{"json": {"a": "a", "b": "foo"}}]),
    ],
)
def test_execute_query_json_dumps(
    psycopg2_connector_factory, mocker, method_name, expected
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
    connector = psycopg2_connector_factory(json_dumps=json_dumps)
    method = getattr(connector, method_name)

    result = method(query, arg=arg)
    assert result == expected


def test_json_loads(psycopg2_connector_factory, mocker):
    # sync json_loads is only used for CLI defer.
    loads = mocker.Mock()
    connector = psycopg2_connector_factory(json_loads=loads)
    assert connector.json_loads is loads


async def test_wrap_exceptions(psycopg2_connector):
    psycopg2_connector.execute_query(
        """SELECT procrastinate_defer_jobs_v1(
            ARRAY[
                ROW(
                    'queue'::character varying,
                    'foo'::character varying,
                    0::integer,
                    NULL::text,
                    'same_queueing_lock'::text,
                    '{}'::jsonb,
                    NULL::timestamptz
                )
            ]::procrastinate_job_to_defer_v1[]
        ) AS id;"""
    )
    with pytest.raises(exceptions.UniqueViolation) as excinfo:
        psycopg2_connector.execute_query(
            """SELECT procrastinate_defer_jobs_v1(
                ARRAY[
                    ROW(
                        'queue'::character varying,
                        'foo'::character varying,
                        0::integer,
                        NULL::text,
                        'same_queueing_lock'::text,
                        '{}'::jsonb,
                        NULL::timestamptz
                    )
                ]::procrastinate_job_to_defer_v1[]
            ) AS id;"""
        )
    assert excinfo.value.constraint_name == manager.QUEUEING_LOCK_CONSTRAINT
    assert excinfo.value.queueing_lock == "same_queueing_lock"


def test_execute_query(psycopg2_connector):
    psycopg2_connector.execute_query("COMMENT ON TABLE \"procrastinate_jobs\" IS 'foo'")
    result = psycopg2_connector.execute_query_one(
        "SELECT obj_description('public.procrastinate_jobs'::regclass)"
    )
    assert result == {"obj_description": "foo"}

    result = psycopg2_connector.execute_query_all(
        "SELECT obj_description('public.procrastinate_jobs'::regclass)"
    )
    assert result == [{"obj_description": "foo"}]


def test_execute_query_arg(psycopg2_connector):
    psycopg2_connector.execute_query("SELECT %(arg)s", arg=1)
    result = psycopg2_connector.execute_query_one("SELECT %(arg)s", arg=1)
    assert result == {"?column?": 1}

    result = psycopg2_connector.execute_query_all("SELECT %(arg)s", arg=1)
    assert result == [{"?column?": 1}]


def test_close(psycopg2_connector):
    pool = psycopg2_connector._pool
    psycopg2_connector.close()
    assert pool.closed is True
