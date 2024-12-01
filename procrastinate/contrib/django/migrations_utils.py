from __future__ import annotations

import functools
from typing import TYPE_CHECKING

from django.db import migrations

if TYPE_CHECKING:
    import importlib_resources
else:
    # https://github.com/pypa/twine/pull/551
    import importlib.resources as importlib_resources


@functools.cache
def list_migration_files() -> dict[str, str]:
    """
    Returns a list of filenames and file contents for all migration files
    """
    return {
        p.name: p.read_text(encoding="utf-8")
        for p in importlib_resources.files("procrastinate.sql.migrations").iterdir()
        if p.name.endswith(".sql")
    }


class RunProcrastinateSQL(migrations.RunSQL):
    """
    A RunSQL migration that reads the SQL from the procrastinate.sql.migrations package
    """

    def __init__(self, name: str):
        self.name = name
        super().__init__(sql=list_migration_files()[name])
