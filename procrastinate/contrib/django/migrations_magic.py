import itertools
import pathlib
import sys
import types
from importlib import abc, machinery
from typing import Iterable, Iterator, Optional, Tuple

import attr
import importlib_resources
from django.db import migrations

# For a thorough explaination of what this package does, see README.md in the same
# folder

TOP_LEVEL_NAME = "procrastinate.contrib.django.migrations"
VIRTUAL_PATH = "<procrastinate migrations virtual path>"


class ProcrastinateMigrationsImporter(abc.MetaPathFinder, abc.Loader):
    def __init__(self):
        sql_migrations = get_all_migrations()
        self.migrations = {
            mig.name: mig for mig in make_migrations(sql_migrations=sql_migrations)
        }

    def iter_modules(self, prefix):
        return [(mig, False) for mig in self.migrations]

    def exec_module(self, module: types.ModuleType) -> None:
        if module.__name__ == TOP_LEVEL_NAME:
            module.__file__ = "virtual"
            module.__path__.append(VIRTUAL_PATH)  # type: ignore
            return

        migration_cls = self.migrations[module.__name__.split(".")[-1]]
        module.Migration = migration_cls  # type: ignore

    def find_spec(
        self,
        fullname: str,
        *args,
        **kwargs,
    ) -> Optional[machinery.ModuleSpec]:
        if fullname.startswith(TOP_LEVEL_NAME):
            return machinery.ModuleSpec(
                name=fullname, loader=self, is_package=fullname == TOP_LEVEL_NAME
            )
        return None

    def path_hook(self, path: str) -> Optional["ProcrastinateMigrationsImporter"]:
        if path == VIRTUAL_PATH:
            return self
        return None


def load():
    if any(isinstance(e, ProcrastinateMigrationsImporter) for e in sys.meta_path):
        # Our job is already done
        return
    importer = ProcrastinateMigrationsImporter()
    sys.meta_path.append(importer)
    sys.path_hooks.append(importer.path_hook)


def get_sql(filename) -> str:
    return importlib_resources.read_text("procrastinate.sql.migrations", filename)


def list_migration_files() -> Iterable[pathlib.Path]:
    return [
        p
        for p in importlib_resources.files("procrastinate.sql.migrations").iterdir()
        if p.suffix == ".sql"
    ]


def version_from_string(version_str) -> Tuple:
    return tuple(int(e) for e in version_str.split("."))


@attr.dataclass(frozen=True)
class ProcrastinateMigration:
    filename: str
    name: str
    version: Tuple
    index: int

    @classmethod
    def from_path(cls, path: pathlib.Path) -> "ProcrastinateMigration":
        version_str, index, name = path.stem.split("_", 2)
        return cls(
            filename=path.name,
            name=name,
            version=version_from_string(version_str=version_str),
            index=int(index),
        )


def get_all_migrations() -> Iterable[ProcrastinateMigration]:
    all_files = list_migration_files()
    migrations = [ProcrastinateMigration.from_path(path=e) for e in all_files]

    return sorted(migrations, key=lambda x: (x.version, x.index))


def make_migrations(
    sql_migrations: Iterable[ProcrastinateMigration],
):
    previous_migration = None
    counter = itertools.count(1)

    for sql_migration in sql_migrations:
        migration = make_migration(
            sql_migration=sql_migration,
            previous_migration=previous_migration,
            counter=counter,
        )
        previous_migration = migration
        yield migration


def make_migration(
    sql_migration: ProcrastinateMigration,
    previous_migration: Optional[migrations.Migration],
    counter: Iterator[int],
):
    class NewMigration(migrations.Migration):
        initial = previous_migration is None
        operations = [migrations.RunSQL(sql=get_sql(filename=sql_migration.filename))]
        name = f"{next(counter):04d}_{sql_migration.name}"

        if previous_migration:
            dependencies = [("procrastinate", previous_migration.name)]

    return NewMigration
