import contextlib
import datetime
import functools
import itertools
import os
import random
import signal as stdlib_signal
import string
import uuid

import aiopg
import psycopg2
import pytest
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from procrastinate import aiopg_connector as aiopg_connector_module
from procrastinate import app as app_module
from procrastinate import jobs
from procrastinate import psycopg2_connector as psycopg2_connector_module
from procrastinate import schema, testing

# Just ensuring the tests are not polluted by environment
for key in os.environ:
    if key.startswith("PROCRASTINATE_"):
        os.environ.pop(key)


def cursor_execute(cursor, query, *identifiers, format=True):
    if identifiers:
        query = sql.SQL(query).format(
            *(sql.Identifier(identifier) for identifier in identifiers)
        )
    cursor.execute(query)


@contextlib.contextmanager
def db_executor(dbname):
    with contextlib.closing(psycopg2.connect("", dbname=dbname)) as connection:
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
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

    connector = aiopg_connector_module.AiopgConnector(dbname=dbname)
    connector.open()
    schema_manager = schema.SchemaManager(connector=connector)
    schema_manager.apply_schema()
    # We need to close the psycopg2 underlying connection synchronously
    connector.close()

    yield dbname

    db_drop(dbname=dbname)


@pytest.fixture
def connection_params(setup_db, db_factory):
    db_factory(dbname="procrastinate_test", template=setup_db)

    yield {"dsn": "", "dbname": "procrastinate_test"}


@pytest.fixture
async def connection(connection_params):
    async with aiopg.connect(**connection_params) as connection:
        yield connection


@pytest.fixture
async def not_opened_aiopg_connector(connection_params):
    yield aiopg_connector_module.AiopgConnector(**connection_params)


@pytest.fixture
def not_opened_psycopg2_connector(connection_params):
    yield psycopg2_connector_module.Psycopg2Connector(**connection_params)


@pytest.fixture
async def aiopg_connector(not_opened_aiopg_connector):
    await not_opened_aiopg_connector.open_async()
    yield not_opened_aiopg_connector
    await not_opened_aiopg_connector.close_async()


@pytest.fixture
def psycopg2_connector(not_opened_psycopg2_connector):
    not_opened_psycopg2_connector.open()
    yield not_opened_psycopg2_connector
    not_opened_psycopg2_connector.close()


@pytest.fixture
def kill_own_pid():
    def f(signal=stdlib_signal.SIGTERM):
        os.kill(os.getpid(), signal)

    return f


@pytest.fixture
def connector():
    return testing.InMemoryConnector()


@pytest.fixture
def not_opened_app(connector):
    return app_module.App(connector=connector)


@pytest.fixture
def app(not_opened_app):
    with not_opened_app.open() as app:
        yield app


@pytest.fixture
def job_store(app):
    return app.job_store


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


def aware_datetime(
    year, month, day, hour=0, minute=0, second=0, microsecond=0, tz_offset=None,
):
    tzinfo = (
        datetime.timezone(datetime.timedelta(hours=tz_offset))
        if tz_offset
        else datetime.timezone.utc
    )
    return datetime.datetime(
        year, month, day, hour, minute, second, microsecond, tzinfo=tzinfo
    )
