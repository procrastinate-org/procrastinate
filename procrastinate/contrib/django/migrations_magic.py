import itertools
import pathlib
import sys
import types
from importlib import abc, machinery
from typing import Iterable, Iterator, Optional, Tuple, Type

import attr
from django.db import migrations

# https://github.com/pypa/twine/pull/551
if sys.version_info[:2] < (3, 9):  # coverage: exclude
    import importlib_resources
else:  # coverage: exclude
    import importlib.resources as importlib_resources

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
        raise ImportError


def load():
    if any(isinstance(e, ProcrastinateMigrationsImporter) for e in sys.meta_path):
        # Our job is already done
        return
    importer = ProcrastinateMigrationsImporter()
    sys.meta_path.append(importer)
    sys.path_hooks.append(importer.path_hook)


def list_migration_files() -> Iterable[Tuple[str, str]]:
    """
    Returns a list of filenames and file contents for all migration files
    """
    return [
        (p.name, p.read_text())
        for p in importlib_resources.files("procrastinate.sql.migrations").iterdir()
        if p.name.endswith(".sql")
    ]


def version_from_string(version_str) -> Tuple:
    return tuple(int(e) for e in version_str.split("."))


@attr.dataclass(frozen=True)
class ProcrastinateMigration:
    filename: str
    name: str
    version: Tuple
    index: int
    contents: str

    @classmethod
    def from_file(cls, filename: str, contents: str) -> "ProcrastinateMigration":
        path = pathlib.PurePath(filename)
        version_str, index, name = path.stem.split("_", 2)
        return cls(
            filename=path.name,
            name=name,
            version=version_from_string(version_str=version_str),
            index=int(index),
            contents=contents,
        )


def get_all_migrations() -> Iterable[ProcrastinateMigration]:
    all_files = list_migration_files()
    migrations = [
        ProcrastinateMigration.from_file(filename=filename, contents=contents)
        for filename, contents in all_files
    ]

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
    previous_migration: Optional[Type[migrations.Migration]],
    counter: Iterator[int],
) -> Type[migrations.Migration]:
    class NewMigration(migrations.Migration):
        initial = previous_migration is None
        operations = [migrations.RunSQL(sql=sql_migration.contents)]
        name = f"{next(counter):04d}_{sql_migration.name}"

        if previous_migration:
            dependencies = [("procrastinate", previous_migration.name)]

    return NewMigration
