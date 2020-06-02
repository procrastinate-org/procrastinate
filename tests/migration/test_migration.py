import os
import subprocess

import pytest

from procrastinate import aiopg_connector, schema

BASELINE = "0.5.0"


# Pum config file is currently broken (https://github.com/opengisch/pum/issues/5)
# When it's fixed, we can add a config file here, and then get rid of omit_table_dir
@pytest.fixture
def pum():

    env = {**os.environ, "PGSERVICEFILE": "tests/migration/pgservice.ini"}

    def _(command, args: str, omit_table_dir=False):
        first_args = ["pum", command]
        if not omit_table_dir:
            first_args.extend(
                ["--table=public.pum", "--dir=procrastinate/sql/migrations"]
            )
        return subprocess.run(first_args + args.split(), check=True, env=env)

    return _


@pytest.fixture
def schema_database(db_factory, pum):
    dbname = "procrastinate_schema"
    db_factory(dbname=dbname)

    # apply the current procrastinate schema to procrastinate_schema
    connector = aiopg_connector.AiopgConnector(dbname=dbname)
    schema_manager = schema.SchemaManager(connector=connector)
    schema_manager.apply_schema()
    connector.close()

    # set the baseline version in procrastinate_schema
    # This db is as far as can be.
    pum("baseline", f"--pg_service {dbname} --baseline 999.999.999")

    return dbname


@pytest.fixture
def migrations_database(db_factory, db_execute, pum):
    dbname = "procrastinate_migrations"
    db_factory(dbname=dbname)

    # apply the baseline schema to procrastinate_migrations
    with db_execute(dbname) as execute:
        with open(f"procrastinate/sql/migrations/baseline-{BASELINE}.sql") as file:
            execute(file.read())

    # set the baseline version in procrastinate_migrations
    pum("baseline", f"--pg_service {dbname} --baseline {BASELINE}")

    return dbname


def test_migration(schema_database, migrations_database, pum):
    # apply the migrations on the migrations_database database
    pum("upgrade", f"--pg_service {migrations_database}")

    # check that the schema_database and migrations_database have
    # the same schema
    proc = pum(
        "check",
        f"--pg_service1={schema_database} --pg_service2={migrations_database} "
        "--verbose_level=2",
        omit_table_dir=True,
    )

    # pum check exits with a non-zero return code if the databases don't have
    # the same schema
    assert proc.returncode == 0
