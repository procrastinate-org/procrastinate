from __future__ import annotations

from django.db import migrations as django_migrations

from procrastinate.contrib.django import migrations_utils


def test_list_migration_files():
    migrations = migrations_utils.list_migration_files()
    migration = migrations["00.00.00_01_initial.sql"]
    assert migration.startswith(
        "CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;"
    )
    assert len(migration.splitlines()) == 187

    assert "__init__.py" not in migrations


def test_RunProcrastinateSQL():
    operation = migrations_utils.RunProcrastinateSQL(name="00.00.00_01_initial.sql")
    assert isinstance(operation, django_migrations.RunSQL)
    assert operation.sql.startswith(
        "CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;"
    )
