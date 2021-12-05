import sys
import types

import pytest
from django.db import migrations as django_migrations

from procrastinate.contrib.django import migrations_magic


def test_version_from_string():
    assert migrations_magic.version_from_string("1.2.3") == (1, 2, 3)


def test_procrastinate_migration_from_file():

    migration = migrations_magic.ProcrastinateMigration.from_file(
        filename="b/00.11.00_03_add_procrastinate_periodic_defers.sql",
        contents="foo",
    )

    assert migration == migrations_magic.ProcrastinateMigration(
        filename="00.11.00_03_add_procrastinate_periodic_defers.sql",
        name="add_procrastinate_periodic_defers",
        version=(0, 11, 0),
        index=3,
        contents="foo",
    )


def test_get_all_migrations():
    migrations = migrations_magic.get_all_migrations()
    assert migrations[0].name == "initial"


def test_make_migration(mocker):
    previous = mocker.Mock()
    previous.name = "0001_foo"
    migration = migrations_magic.make_migration(
        sql_migration=migrations_magic.ProcrastinateMigration.from_file(
            filename="a/00.08.01_01_add_queueing_lock_column.sql",
            contents="SELECT 1;",
        ),
        previous_migration=previous,
        counter=iter([2]),
    )
    assert migration.name == "0002_add_queueing_lock_column"
    assert migration.dependencies == [("procrastinate", "0001_foo")]
    assert migration.initial is False
    assert len(migration.operations) == 1
    assert migration.operations[0].sql == "SELECT 1;"


def test_make_migration_initial():
    migration = migrations_magic.make_migration(
        sql_migration=migrations_magic.ProcrastinateMigration.from_file(
            filename="a/00.00.00_01_initial.sql",
            contents="SELECT 1;",
        ),
        previous_migration=None,
        counter=iter([1]),
    )
    assert migration.name == "0001_initial"
    assert migration.dependencies == []
    assert migration.initial is True
    assert migration.operations[0].sql == "SELECT 1;"


def test_list_migration_files():
    migrations = dict(migrations_magic.list_migration_files())
    migration = migrations["00.00.00_01_initial.sql"]
    assert migration.startswith(
        "CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;"
    )
    assert len(migration.splitlines()) == 187

    assert "__init__.py" not in migrations


@pytest.fixture
def importer():
    return migrations_magic.ProcrastinateMigrationsImporter()


def test_importer(importer):
    assert issubclass(importer.migrations["0001_initial"], django_migrations.Migration)


def test_importer_iter_modules(importer):
    assert importer.iter_modules(prefix="")[0] == ("0001_initial", False)


def test_importer_exec_module_top_level(importer):
    module = types.ModuleType(name="procrastinate.contrib.django.migrations")
    module.__path__ = []

    importer.exec_module(module)

    assert module.__file__ == "virtual"
    assert module.__path__ == ["<procrastinate migrations virtual path>"]


def test_importer_exec_module_migration(importer):
    module = types.ModuleType(
        name="procrastinate.contrib.django.migrations.0001_initial"
    )

    importer.exec_module(module)

    assert module.Migration.name == "0001_initial"


@pytest.mark.parametrize(
    "name, is_package",
    [
        ("procrastinate.contrib.django.migrations", True),
        ("procrastinate.contrib.django.migrations.0001_initial", False),
    ],
)
def test_importer_exec_find_spec(importer, name, is_package):
    spec = importer.find_spec(fullname=name)

    assert spec.name == name
    assert spec.loader is importer
    # We can't check directly the is_package value, but this is a side-effect:
    assert spec.submodule_search_locations == ([] if is_package else None)


def test_importer_exec_find_spec_other_package(importer):
    assert importer.find_spec("pytest") is None


def test_importer_path_hook(importer):
    assert (
        importer.path_hook(path="<procrastinate migrations virtual path>") is importer
    )


def test_importer_path_hook_other_package(importer):
    with pytest.raises(ImportError):
        importer.path_hook("/some/other/path")


@pytest.fixture
def clean_paths(mocker):
    mocker.patch.object(sys, "meta_path", [])
    mocker.patch.object(sys, "path_hooks", [])


def test_load(clean_paths):
    migrations_magic.load()
    assert isinstance(
        sys.meta_path[0], migrations_magic.ProcrastinateMigrationsImporter
    )
    hook_name = "ProcrastinateMigrationsImporter.path_hook"
    assert hook_name == sys.path_hooks[0].__qualname__


def test_load_again(clean_paths):
    migrations_magic.load()
    assert len(sys.meta_path) == 1
    migrations_magic.load()

    # Making sure we don't add our elements to the path twice
    assert len(sys.meta_path) == 1
