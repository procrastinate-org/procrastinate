import pathlib
import sys
import types

import pytest
from django.db import migrations as django_migrations

from procrastinate.contrib.django import migrations_magic


def test_version_from_string():
    assert migrations_magic.version_from_string("1.2.3") == (1, 2, 3)


@pytest.mark.parametrize(
    "path, expected",
    [
        (
            "a/baseline-0.5.0.sql",
            migrations_magic.ProcrastinateMigration(
                filename="baseline-0.5.0.sql",
                name="baseline",
                version=(0, 5, 0),
                index=0,
            ),
        ),
        (
            "b/delta_0.11.0_003_add_procrastinate_periodic_defers.sql",
            migrations_magic.ProcrastinateMigration(
                filename="delta_0.11.0_003_add_procrastinate_periodic_defers.sql",
                name="add_procrastinate_periodic_defers",
                version=(0, 11, 0),
                index=3,
            ),
        ),
    ],
)
def test_procrastinate_migration_from_path(path, expected):
    migration = migrations_magic.ProcrastinateMigration.from_path(pathlib.Path(path))

    assert migration == expected


def test_get_all_migrations():
    migrations = migrations_magic.get_all_migrations()
    assert migrations[0].name == "baseline"


def test_make_migration(mocker):
    previous = mocker.Mock()
    previous.name = "0001_foo"
    migration = migrations_magic.make_migration(
        sql_migration=migrations_magic.ProcrastinateMigration.from_path(
            path=pathlib.Path("a/delta_0.8.1_001_add_queueing_lock_column.sql")
        ),
        previous_migration=previous,
        counter=iter([2]),
    )
    assert migration.name == "0002_add_queueing_lock_column"
    assert migration.dependencies == [("procrastinate", "0001_foo")]
    assert migration.initial is False
    assert len(migration.operations) == 1
    assert migration.operations[0].sql.startswith("-- add a queueing_lock column")


def test_make_migration_initial():
    migration = migrations_magic.make_migration(
        sql_migration=migrations_magic.ProcrastinateMigration.from_path(
            path=pathlib.Path("a/baseline-0.5.0.sql")
        ),
        previous_migration=None,
        counter=iter([1]),
    )
    assert migration.name == "0001_baseline"
    assert migration.dependencies == []
    assert migration.initial is True


def test_get_sql(app):
    migration_name = "baseline-0.5.0.sql"
    migration = migrations_magic.get_sql(migration_name)

    assert migration.startswith(
        "CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;"
    )
    assert len(migration.splitlines()) == 187


def test_list_migration_files():
    names = {e.name for e in migrations_magic.list_migration_files()}
    assert "baseline-0.5.0.sql" in names
    assert "__init__.py" not in names


@pytest.fixture
def importer():
    return migrations_magic.ProcrastinateMigrationsImporter()


def test_importer(importer):
    assert issubclass(importer.migrations["0001_baseline"], django_migrations.Migration)


def test_importer_iter_modules(importer):
    assert importer.iter_modules(prefix="")[0] == ("0001_baseline", False)


def test_importer_exec_module_top_level(importer):
    module = types.ModuleType(name="procrastinate.contrib.django.migrations")
    module.__path__ = []

    importer.exec_module(module)

    assert module.__file__ == "virtual"
    assert module.__path__ == ["<procrastinate migrations virtual path>"]


def test_importer_exec_module_migration(importer):
    module = types.ModuleType(
        name="procrastinate.contrib.django.migrations.0001_baseline"
    )

    importer.exec_module(module)

    assert module.Migration.name == "0001_baseline"


@pytest.mark.parametrize(
    "name, is_package",
    [
        ("procrastinate.contrib.django.migrations", True),
        ("procrastinate.contrib.django.migrations.0001_baseline", False),
    ],
)
def test_importer_exec_find_spec(importer, name, is_package):
    spec = importer.find_spec(fullname=name)

    assert spec.name == name
    assert spec.loader is importer
    assert spec.submodule_search_locations == ([] if is_package else None)


def test_importer_exec_find_spec_other_package(importer):
    assert importer.find_spec("pytest") is None


def test_importer_path_hook(importer):
    assert (
        importer.path_hook(path="<procrastinate migrations virtual path>") is importer
    )


def test_importer_path_hook_other_package(importer):
    assert importer.path_hook("/some/other/path") is None


@pytest.fixture
def clean_paths(mocker):
    mocker.patch.object(sys, "meta_path", [])
    mocker.patch.object(sys, "path_hooks", [])


def test_load(clean_paths):
    migrations_magic.load()
    assert isinstance(
        sys.meta_path[-1], migrations_magic.ProcrastinateMigrationsImporter
    )
    hook_name = "ProcrastinateMigrationsImporter.path_hook"
    assert hook_name == sys.path_hooks[-1].__qualname__


def test_load_again(clean_paths):
    migrations_magic.load()
    old_len = len(sys.meta_path)
    migrations_magic.load()
    assert len(sys.meta_path) == old_len
