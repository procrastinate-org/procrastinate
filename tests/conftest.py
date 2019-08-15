import os
import signal as stdlib_signal
from contextlib import closing

import psycopg2
import pytest
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from procrastinate import app as app_module
from procrastinate import jobs, postgres, testing


def _execute(cursor, query, *identifiers):
    cursor.execute(
        sql.SQL(query).format(
            *(sql.Identifier(identifier) for identifier in identifiers)
        )
    )


@pytest.fixture(scope="session")
def setup_db():

    with closing(psycopg2.connect("", dbname="postgres")) as connection:
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with connection.cursor() as cursor:
            _execute(
                cursor, "DROP DATABASE IF EXISTS {}", "procrastinate_test_template"
            )
            _execute(cursor, "CREATE DATABASE {}", "procrastinate_test_template")

    with closing(
        psycopg2.connect("", dbname="procrastinate_test_template")
    ) as connection:
        with connection.cursor() as cursor:
            with open("init.sql") as migrations:
                cursor.execute(migrations.read())
        connection.commit()
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        yield connection

    with closing(psycopg2.connect("", dbname="postgres")) as connection:
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with connection.cursor() as cursor:
            _execute(
                cursor, "DROP DATABASE IF EXISTS {}", "procrastinate_test_template"
            )


@pytest.fixture
def connection_params(setup_db):
    with setup_db.cursor() as cursor:
        _execute(cursor, "DROP DATABASE IF EXISTS {}", "procrastinate_test")
        _execute(
            cursor,
            "CREATE DATABASE {} TEMPLATE {}",
            "procrastinate_test",
            "procrastinate_test_template",
        )

    yield {"dsn": "", "dbname": "procrastinate_test"}

    with setup_db.cursor() as cursor:
        _execute(cursor, "DROP DATABASE IF EXISTS {}", "procrastinate_test")


@pytest.fixture
def connection(connection_params):
    with closing(psycopg2.connect(**connection_params)) as connection:
        yield connection


@pytest.fixture
def pg_job_store(connection_params):
    job_store = postgres.PostgresJobStore(**connection_params)
    yield job_store
    job_store.connection.close()


@pytest.fixture
def kill_own_pid():
    def f(signal=stdlib_signal.SIGTERM):
        os.kill(os.getpid(), signal)

    return f


@pytest.fixture
def job_store():
    return testing.InMemoryJobStore()


@pytest.fixture
def app(job_store):
    return app_module.App(job_store=job_store)


@pytest.fixture
def job_factory(job_store):
    defaults = {
        "id": 42,
        "task_name": "bla",
        "task_kwargs": {},
        "lock": None,
        "queue": "queue",
        "job_store": job_store,
    }

    def factory(**kwargs):
        final_kwargs = defaults.copy()
        final_kwargs.update(kwargs)
        return jobs.Job(**final_kwargs)

    return factory
