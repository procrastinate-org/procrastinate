import os

from procrastinate.contrib.django import utils


def test_get_sql(app):
    migration_name = "baseline-0.5.0.sql"
    migration = utils.get_sql(migration_name)

    assert migration.startswith(
        "CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;"
    )
    assert len(migration.splitlines()) == 187


def test_list_migrations():
    names = {e.name for e in utils.list_migrations()}
    assert "baseline-0.5.0.sql" in names
    assert "__init__.py" not in names


def test_run_procrastinate_file_init():
    operation = utils.RunProcrastinateFile(filename="baseline-0.5.0.sql")
    assert operation.filename == "baseline-0.5.0.sql"
    assert operation.sql.startswith(
        "CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;"
    )


def test_run_procrastinate_file_deconstruct():
    operation = utils.RunProcrastinateFile(filename="baseline-0.5.0.sql")
    assert operation.deconstruct() == (
        "RunProcrastinateFile",
        [],
        {"filename": "baseline-0.5.0.sql"},
    )


def test_run_procrastinate_file_describe():
    operation = utils.RunProcrastinateFile(filename="baseline-0.5.0.sql")
    assert operation.describe() == "Procrastinate SQL migration: baseline-0.5.0.sql"


def test_connector_params():
    assert "database" in utils.connector_params()
