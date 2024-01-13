import contextlib
import datetime
import functools
import itertools
import os
import random
import signal as stdlib_signal
import string
import uuid

import psycopg
import psycopg.conninfo
import psycopg.sql
import pytest

from procrastinate import app as app_module
from procrastinate import blueprints, builtin_tasks, jobs
from procrastinate import psycopg_connector as async_psycopg_connector_module
from procrastinate import schema
from procrastinate import sync_psycopg_connector as sync_psycopg_connector_module
from procrastinate import testing

# Just ensuring the tests are not polluted by environment
for key in os.environ:
    if key.startswith("PROCRASTINATE_"):
        os.environ.pop(key)


def cursor_execute(cursor, query, *identifiers):
    if identifiers:
        query = psycopg.sql.SQL(query).format(
            *(psycopg.sql.Identifier(identifier) for identifier in identifiers)
        )
    cursor.execute(query)


@contextlib.contextmanager
def db_executor(dbname):
    with psycopg.connect("", dbname=dbname, autocommit=True) as connection:
        with connection.cursor() as cursor:
            yield functools.partial(cursor_execute, cursor)


@pytest.fixture
def db_execute():
    return db_executor


def db_create(dbname, template=None):
    with db_executor("postgres") as execute:
        execute("DROP DATABASE IF EXISTS {}", dbname)
        if template:
            execute("CREATE DATABASE {} TEMPLATE {}", dbname, template)
        else:
            execute("CREATE DATABASE {}", dbname)


def db_drop(dbname):
    with db_executor("postgres") as execute:
        execute("DROP DATABASE IF EXISTS {}", dbname)


@pytest.fixture
def db_factory():
    dbs_to_drop = []

    def _(dbname, template=None):
        db_create(dbname=dbname, template=template)
        dbs_to_drop.append(dbname)

    yield _

    for dbname in dbs_to_drop:
        db_drop(dbname=dbname)


@pytest.fixture(scope="session")
def setup_db():
    dbname = "procrastinate_test_template"
    db_create(dbname=dbname)
    connector = testing.InMemoryConnector()

    with db_executor(dbname) as execute:
        execute(schema.SchemaManager(connector=connector).get_schema())

    yield dbname

    db_drop(dbname=dbname)


@pytest.fixture
def connection_params(setup_db, db_factory):
    db_factory(dbname="procrastinate_test", template=setup_db)

    return {"dbname": "procrastinate_test"}


@pytest.fixture
def make_psycopg_connection_params():
    def _(**kwargs):
        return {"conninfo": psycopg.conninfo.make_conninfo(**kwargs)}

    return _


@pytest.fixture
def psycopg_connection_params(connection_params, make_psycopg_connection_params):
    yield make_psycopg_connection_params(**connection_params)


@pytest.fixture
async def not_opened_psycopg_connector(psycopg_connection_params):
    yield async_psycopg_connector_module.PsycopgConnector(**psycopg_connection_params)


@pytest.fixture
def not_opened_sync_psycopg_connector(psycopg_connection_params):
    yield sync_psycopg_connector_module.SyncPsycopgConnector(
        **psycopg_connection_params
    )


@pytest.fixture
async def psycopg_connector(not_opened_psycopg_connector):
    await not_opened_psycopg_connector.open_async()
    yield not_opened_psycopg_connector
    await not_opened_psycopg_connector.close_async()


@pytest.fixture
def sync_psycopg_connector(not_opened_sync_psycopg_connector):
    not_opened_sync_psycopg_connector.open()
    yield not_opened_sync_psycopg_connector
    not_opened_sync_psycopg_connector.close()


@pytest.fixture
def sqlalchemy_psycopg2_connector(not_opened_sqlalchemy_psycopg2_connector):
    not_opened_sqlalchemy_psycopg2_connector.open()
    yield not_opened_sqlalchemy_psycopg2_connector
    not_opened_sqlalchemy_psycopg2_connector.close()


@pytest.fixture
def kill_own_pid():
    def f(signal=stdlib_signal.SIGTERM):
        os.kill(os.getpid(), signal)

    return f


@pytest.fixture
def connector():
    return testing.InMemoryConnector()


@pytest.fixture
def reset_builtin_task_names():
    builtin_tasks.remove_old_jobs.name = "procrastinate.builtin_tasks.remove_old_jobs"
    builtin_tasks.builtin.tasks = {
        task.name: task for task in builtin_tasks.builtin.tasks.values()
    }


@pytest.fixture
def not_opened_app(connector, reset_builtin_task_names):
    return app_module.App(connector=connector)


@pytest.fixture
def app(not_opened_app):
    with not_opened_app.open() as app:
        yield app


@pytest.fixture
def blueprint():
    return blueprints.Blueprint()


@pytest.fixture
def job_manager(app):
    return app.job_manager


@pytest.fixture
def serial():
    return itertools.count(1)


@pytest.fixture
def random_str():
    def _(length=8):
        return "".join(random.choice(string.ascii_lowercase) for _ in range(length))

    return _


@pytest.fixture
def job_factory(serial, random_str):
    def factory(**kwargs):
        defaults = {
            "id": next(serial),
            "task_name": f"task_{random_str()}",
            "task_kwargs": {},
            "lock": str(uuid.uuid4()),
            "queueing_lock": None,
            "queue": f"queue_{random_str()}",
        }
        final_kwargs = defaults.copy()
        final_kwargs.update(kwargs)
        return jobs.Job(**final_kwargs)

    return factory


@pytest.fixture
def deferred_job_factory(job_factory, job_manager):
    async def factory(*, job_manager=job_manager, **kwargs):
        job = job_factory(id=None, **kwargs)
        return await job_manager.defer_job_async(job)

    return factory


def aware_datetime(
    year, month, day, hour=0, minute=0, second=0, microsecond=0, tz_offset=None
):
    tzinfo = (
        datetime.timezone(datetime.timedelta(hours=tz_offset))
        if tz_offset
        else datetime.timezone.utc
    )
    return datetime.datetime(
        year, month, day, hour, minute, second, microsecond, tzinfo=tzinfo
    )
