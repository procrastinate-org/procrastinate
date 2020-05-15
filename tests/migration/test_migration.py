import os
import subprocess
from contextlib import closing

import pkg_resources
import psycopg2
import pytest
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from procrastinate import __version__, aiopg_connector, schema

PG_SERVICES = """
[procrastinate_test1]
dbname=procrastinate_test1
[procrastinate_test2]
dbname=procrastinate_test2
"""


def _execute_sql(cursor, query, *identifiers):
    cursor.execute(
        sql.SQL(query).format(
            *(sql.Identifier(identifier) for identifier in identifiers)
        )
    )


@pytest.fixture
def migrations_directory():
    return pkg_resources.resource_filename("procrastinate", "sql/migrations")


@pytest.fixture
def procrastinate_version():
    try:
        idx = __version__.index("+")
    except ValueError:
        idx = None
    return __version__[:idx]


@pytest.fixture
def pg_service_file(tmp_path):
    file_path = tmp_path / "pg_service.conf"
    with open(file_path, "w") as file_:
        file_.write(PG_SERVICES)
    yield file_path


@pytest.fixture
def environment(pg_service_file):
    env = os.environ.copy()
    env["PGSERVICEFILE"] = pg_service_file
    return env


@pytest.fixture
def setup_databases(procrastinate_version, migrations_directory, environment):

    # create the procrastinate_test1 and procrastinate_test2 databases
    with closing(psycopg2.connect("", dbname="postgres")) as connection:
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with connection.cursor() as cursor:
            _execute_sql(cursor, "DROP DATABASE IF EXISTS {}", "procrastinate_test1")
            _execute_sql(cursor, "CREATE DATABASE {}", "procrastinate_test1")
            _execute_sql(cursor, "DROP DATABASE IF EXISTS {}", "procrastinate_test2")
            _execute_sql(cursor, "CREATE DATABASE {}", "procrastinate_test2")

    # apply the procrastinate schema to procrastinate_test1
    connector = aiopg_connector.PostgresConnector(dbname="procrastinate_test1")
    schema_manager = schema.SchemaManager(connector=connector)
    schema_manager.apply_schema()
    connector.close()

    # set the baseline version in procrastinate_test1
    cmd = (
        "pum baseline -p procrastinate_test1 -t public.pum "
        f"-d {migrations_directory} -b {procrastinate_version}"
    )
    subprocess.run(cmd.split(), check=True, env=environment)

    # apply the baseline schema to procrastinate_test2
    cmd = f"psql -d procrastinate_test2 -f {migrations_directory}/baseline-0.5.0.sql"
    subprocess.run(cmd.split(), check=True)

    # set the baseline version in procrastinate_test2
    cmd = (
        f"pum baseline -p procrastinate_test2 -t public.pum -d {migrations_directory} "
        "-b 0.5.0"
    )
    subprocess.run(cmd.split(), check=True, env=environment)

    yield

    with closing(psycopg2.connect("", dbname="postgres")) as connection:
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with connection.cursor() as cursor:
            _execute_sql(cursor, "DROP DATABASE IF EXISTS {}", "procrastinate_test2")
            _execute_sql(cursor, "DROP DATABASE IF EXISTS {}", "procrastinate_test1")


def test_migration(setup_databases, migrations_directory, environment):
    # apply the migrations on the procrastinate_test2 database
    cmd = f"pum upgrade -p procrastinate_test2 -t public.pum -d {migrations_directory}"
    subprocess.run(cmd.split(), check=True, env=environment)

    # check that the databases procrastinate_test1 and procrastinate_test2 have
    # the same schema
    cmd = "pum check -p1 procrastinate_test1 -p2 procrastinate_test2 -v 2"
    proc = subprocess.run(cmd.split(), env=environment, stdout=True, stderr=True)

    # pum check exits with a non-zero return code if the databases don't have
    # the same schema
    assert proc.returncode == 0
