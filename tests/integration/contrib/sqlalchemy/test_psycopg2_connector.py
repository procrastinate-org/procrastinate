from __future__ import annotations

import functools
import json

import psycopg2.errors
import pytest

from procrastinate import exceptions, manager
from procrastinate.contrib.sqlalchemy import SQLAlchemyPsycopg2Connector


@pytest.fixture
def sqlalchemy_engine_dsn(connection_params):
    yield f"postgresql+psycopg2:///{connection_params['dbname']}"


@pytest.fixture
def sqlalchemy_psycopg2_connector_factory(sqlalchemy_engine_dsn):
    connectors = []

    def _(**kwargs):
        json_dumps = kwargs.pop("json_dumps", None)
        json_loads = kwargs.pop("json_loads", None)
        engine_params = kwargs
        connector = SQLAlchemyPsycopg2Connector(
            dsn=sqlalchemy_engine_dsn,
            json_dumps=json_dumps,
            json_loads=json_loads,
            **engine_params,
        )
        connectors.append(connector)
        connector.open()
        return connector

    yield _
    for connector in connectors:
        connector.close()


@pytest.fixture
def not_opened_sqlalchemy_psycopg2_connector(sqlalchemy_engine_dsn):
    return SQLAlchemyPsycopg2Connector(dsn=sqlalchemy_engine_dsn)


def test_connection(sqlalchemy_psycopg2_connector_factory, sqlalchemy_engine_dsn):
    connector = sqlalchemy_psycopg2_connector_factory()
    with connector.engine.connect() as connection:
        assert connection.engine.url.render_as_string() == sqlalchemy_engine_dsn


@pytest.mark.parametrize("exception", [Exception, psycopg2.errors.AdminShutdown])
def test_connection_exception(sqlalchemy_psycopg2_connector_factory, exception):
    connector = sqlalchemy_psycopg2_connector_factory()
    with pytest.raises(exception):
        with connector.engine.begin():
            raise exception


@pytest.mark.parametrize(
    "method_name, expected",
    [
        ("execute_query_one", {"json": {"a": "a", "b": "foo"}}),
        ("execute_query_all", [{"json": {"a": "a", "b": "foo"}}]),
    ],
)
def test_execute_query_json_dumps(
    sqlalchemy_psycopg2_connector_factory, mocker, method_name, expected
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
    connector = sqlalchemy_psycopg2_connector_factory(json_dumps=json_dumps)
    method = getattr(connector, method_name)

    result = method(query, arg=arg)
    assert result == expected


def test_json_loads(sqlalchemy_psycopg2_connector_factory, mocker):
    # sync json_loads is only used for CLI defer.
    loads = mocker.Mock()
    connector = sqlalchemy_psycopg2_connector_factory(json_loads=loads)
    assert connector.json_loads is loads


async def test_wrap_exceptions(sqlalchemy_psycopg2_connector):
    sqlalchemy_psycopg2_connector.execute_query(
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
        sqlalchemy_psycopg2_connector.execute_query(
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


def test_execute_query(sqlalchemy_psycopg2_connector):
    sqlalchemy_psycopg2_connector.execute_query(
        "COMMENT ON TABLE \"procrastinate_jobs\" IS 'foo'"
    )
    result = sqlalchemy_psycopg2_connector.execute_query_one(
        "SELECT obj_description('public.procrastinate_jobs'::regclass)"
    )
    assert result == {"obj_description": "foo"}

    result = sqlalchemy_psycopg2_connector.execute_query_all(
        "SELECT obj_description('public.procrastinate_jobs'::regclass)"
    )
    assert result == [{"obj_description": "foo"}]


def test_execute_query_arg(sqlalchemy_psycopg2_connector):
    sqlalchemy_psycopg2_connector.execute_query("SELECT %(arg)s", arg=1)
    result = sqlalchemy_psycopg2_connector.execute_query_one("SELECT %(arg)s", arg=1)
    assert result == {"?column?": 1}

    result = sqlalchemy_psycopg2_connector.execute_query_all("SELECT %(arg)s", arg=1)
    assert result == [{"?column?": 1}]


def test_close(sqlalchemy_psycopg2_connector):
    sqlalchemy_psycopg2_connector.execute_query("SELECT 1")
    engine = sqlalchemy_psycopg2_connector.engine
    assert engine.pool.checkedin() == 1
    sqlalchemy_psycopg2_connector.close()
    assert engine.pool.checkedin() == 0
