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


def test_execute_query_all_with_connection(sync_psycopg_connector):
    with sync_psycopg_connector.pool.connection() as conn:
        result = sync_psycopg_connector.execute_query_all_with_connection(
            conn, "SELECT %(arg)s as col", arg=1
        )
    assert result == [{"col": 1}]


def test_defer_with_external_connection_commit(
    sync_psycopg_connector, connection_params
):
    import psycopg

    from procrastinate import App, sql

    app = App(connector=sync_psycopg_connector)
    app.open()

    @app.task
    def my_task(x):
        pass

    conninfo = psycopg.conninfo.make_conninfo(**connection_params)
    with psycopg.connect(conninfo) as conn:
        conn.autocommit = False
        my_task.configure(connection=conn).defer(x=1)
        conn.commit()

    # Job should be in DB after commit
    jobs = sync_psycopg_connector.execute_query_all(
        query=sql.queries["list_jobs"],
        id=None,
        queue_name=None,
        task_name=None,
        status=None,
        lock=None,
        queueing_lock=None,
        worker_id=None,
    )
    assert len(jobs) >= 1
    assert any(
        j["task_name"] == "tests.integration.test_sync_psycopg_connector.my_task"
        for j in jobs
    )


def test_defer_with_external_connection_rollback(
    sync_psycopg_connector, connection_params
):
    import psycopg

    from procrastinate import App, sql

    app = App(connector=sync_psycopg_connector)
    app.open()

    @app.task
    def my_rollback_task(x):
        pass

    conninfo = psycopg.conninfo.make_conninfo(**connection_params)
    with psycopg.connect(conninfo) as conn:
        conn.autocommit = False
        my_rollback_task.configure(connection=conn).defer(x=1)
        conn.rollback()

    # Job should NOT be in DB after rollback
    jobs = sync_psycopg_connector.execute_query_all(
        query=sql.queries["list_jobs"],
        id=None,
        queue_name=None,
        task_name="tests.integration.test_sync_psycopg_connector.my_rollback_task",
        status=None,
        lock=None,
        queueing_lock=None,
        worker_id=None,
    )
    assert len(jobs) == 0


def test_batch_defer_with_external_connection_commit(
    sync_psycopg_connector, connection_params
):
    import psycopg

    from procrastinate import App, sql

    app = App(connector=sync_psycopg_connector)
    app.open()

    @app.task
    def my_batch_task(x):
        pass

    conninfo = psycopg.conninfo.make_conninfo(**connection_params)
    with psycopg.connect(conninfo) as conn:
        conn.autocommit = False
        my_batch_task.configure(connection=conn).batch_defer({"x": 1}, {"x": 2})
        conn.commit()

    jobs = sync_psycopg_connector.execute_query_all(
        query=sql.queries["list_jobs"],
        id=None,
        queue_name=None,
        task_name=None,
        status=None,
        lock=None,
        queueing_lock=None,
        worker_id=None,
    )
    assert len(jobs) >= 2
    assert (
        sum(
            j["task_name"]
            == "tests.integration.test_sync_psycopg_connector.my_batch_task"
            for j in jobs
        )
        == 2
    )


def test_batch_defer_with_external_connection_rollback(
    sync_psycopg_connector, connection_params
):
    import psycopg

    from procrastinate import App, sql

    app = App(connector=sync_psycopg_connector)
    app.open()

    @app.task
    def my_batch_rollback_task(x):
        pass

    conninfo = psycopg.conninfo.make_conninfo(**connection_params)
    with psycopg.connect(conninfo) as conn:
        conn.autocommit = False
        my_batch_rollback_task.configure(connection=conn).batch_defer(
            {"x": 1}, {"x": 2}
        )
        conn.rollback()

    jobs = sync_psycopg_connector.execute_query_all(
        query=sql.queries["list_jobs"],
        id=None,
        queue_name=None,
        task_name="tests.integration.test_sync_psycopg_connector.my_batch_rollback_task",
        status=None,
        lock=None,
        queueing_lock=None,
        worker_id=None,
    )
    assert len(jobs) == 0
