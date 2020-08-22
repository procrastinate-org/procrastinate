import pathlib
from typing import Any, Dict, Iterable

import importlib_resources
from django.db import connections, migrations


def get_sql(filename) -> str:
    return importlib_resources.read_text("procrastinate.sql.migrations", filename)


def list_migrations() -> Iterable[pathlib.Path]:
    return [
        p
        for p in importlib_resources.files("procrastinate.sql.migrations").iterdir()
        if p.suffix == ".sql"
    ]


class RunProcrastinateFile(migrations.RunSQL):
    __module__ = "procrastinate.contrib.django"

    def __init__(self, filename, **kwargs):
        self.filename = filename
        self.sql = get_sql(filename=filename)
        super().__init__(sql=self.sql, **kwargs)

    def deconstruct(self):
        qualname, args, kwargs = super().deconstruct()
        kwargs.pop("sql")
        kwargs["filename"] = self.filename

        return qualname, args, kwargs

    def describe(self):
        return f"Procrastinate SQL migration: {self.filename}"


def connector_params(alias: str = "default") -> Dict[str, Any]:
    wrapper = connections[alias]
    return wrapper.get_connection_params()
