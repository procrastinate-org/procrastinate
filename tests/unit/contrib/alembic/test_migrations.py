from __future__ import annotations

import importlib
import pkgutil
from importlib import resources

from procrastinate.contrib.alembic import versions


def test_revisions_follow_sql_migrations():
    revisions = sorted(
        (
            importlib.import_module(f"{versions.__name__}.{module_info.name}")
            for module_info in pkgutil.iter_modules(versions.__path__)
        ),
        key=lambda module: module.revision,
    )
    sql_migrations = sorted(
        p.name
        for p in resources.files("procrastinate.sql.migrations").iterdir()
        if p.name.endswith(".sql")
    )

    assert [revision.MIGRATION_FILE for revision in revisions] == sql_migrations, (
        "If this test fails, you probably need to add an Alembic revision in "
        "procrastinate/contrib/alembic/versions/ referencing a SQL file recently "
        "added in procrastinate/sql/migrations/"
    )
    assert [revision.down_revision for revision in revisions] == [
        None,
        *(revision.revision for revision in revisions[:-1]),
    ], "Each Alembic revision should have the previous one as down_revision"
