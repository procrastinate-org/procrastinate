from __future__ import annotations

import importlib
from pkgutil import iter_modules

from procrastinate.contrib.django import migrations, migrations_utils


def test_no_missing_migration():
    path = next(iter(migrations.__path__))
    file_names = []
    for migration_module_info in iter_modules(path=[path]):
        module = importlib.import_module(
            f"procrastinate.contrib.django.migrations.{migration_module_info.name}"
        )

        migration = getattr(module, "Migration")
        for operation in migration.operations:
            if isinstance(operation, migrations_utils.RunProcrastinateSQL):
                file_names.append(operation.name)

    sql_migrations = [str(e) for e in migrations_utils.list_migration_files()]

    assert set(sql_migrations) == set(file_names), (
        "If this test fails, you probably need to add "
        "a django migration file in procrastinate/contrib/django/migrations/ "
        "referencing a SQL file recently added in procrastinate/sql/migrations/"
    )
    assert len(sql_migrations) == len(file_names), (
        "If this test fails, you probably reference the same SQL migration "
        "file multiple times in the Django migrations in "
        "procrastinate/contrib/django/migrations/"
    )
