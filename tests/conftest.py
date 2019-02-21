import pytest
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from cabbage import postgres


def _execute(cursor, query, *identifiers):
    cursor.execute(
        sql.SQL(query).format(
            *(sql.Identifier(identifier) for identifier in identifiers)
        )
    )


@pytest.fixture(scope="session")
def setup_db():

    with psycopg2.connect("", dbname="postgres") as connection:
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with connection.cursor() as cursor:
            _execute(cursor, "DROP DATABASE IF EXISTS {}", "cabbage_test_template")
            _execute(cursor, "CREATE DATABASE {}", "cabbage_test_template")

    with psycopg2.connect("", dbname="cabbage_test_template") as connection:
        with connection.cursor() as cursor:
            with open("init.sql") as migrations:
                cursor.execute(migrations.read())
        connection.commit()
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        yield connection


@pytest.fixture
def db(setup_db):
    with setup_db.cursor() as cursor:
        _execute(cursor, "DROP DATABASE IF EXISTS {}", "cabbage_test")
        _execute(
            cursor,
            "CREATE DATABASE {} TEMPLATE {}",
            "cabbage_test",
            "cabbage_test_template",
        )
    params = setup_db.get_dsn_parameters()
    params["dbname"] = "cabbage_test"
    with postgres.get_global_connection(**params) as connection:
        yield connection
    postgres.reset_global_connection()
