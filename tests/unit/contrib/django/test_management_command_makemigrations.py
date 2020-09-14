import pathlib

import pytest
from django.db import migrations as django_migrations
from django.db.migrations.loader import MigrationLoader

from procrastinate.contrib.django.management.commands import makemigrations


@pytest.fixture
def loader():
    return MigrationLoader(None, ignore_no_migrations=True)


@pytest.fixture
def disk_migrations(loader):
    return makemigrations.extract_disk_migrations(loader=loader)


def test_get_max_existing_migration(disk_migrations):
    migration = makemigrations.get_max_existing_migration(
        disk_migrations=disk_migrations
    )
    migrations = pathlib.Path("procrastinate/contrib/django/migrations/").glob("0*.py")
    assert migration.name == max(migrations).stem


def test_version_from_string():
    assert makemigrations.version_from_string("1.2.3") == (1, 2, 3)


@pytest.mark.parametrize(
    "path, expected",
    [
        (
            "a/baseline-0.5.0.sql",
            makemigrations.ProcrastinateMigration(
                filename="baseline-0.5.0.sql",
                name="baseline",
                version=(0, 5, 0),
                index=0,
            ),
        ),
        (
            "b/delta_0.11.0_003_add_procrastinate_periodic_defers.sql",
            makemigrations.ProcrastinateMigration(
                filename="delta_0.11.0_003_add_procrastinate_periodic_defers.sql",
                name="add_procrastinate_periodic_defers",
                version=(0, 11, 0),
                index=3,
            ),
        ),
    ],
)
def test_procrastinate_migration_from_path(path, expected):
    migration = makemigrations.ProcrastinateMigration.from_path(pathlib.Path(path))

    assert migration == expected


def test_get_all_migrations():
    migrations = makemigrations.get_all_migrations()
    assert migrations[0].name == "baseline"


def test_get_existing_migrations(disk_migrations):
    disk_migrations["0007_add_queueing_lock_column"].operations.append(
        django_migrations.RunSQL("SELECT 'yay'")
    )
    migrations = set(
        makemigrations.get_existing_migrations(disk_migrations=disk_migrations)
    )
    assert "delta_0.10.0_002_add_defer_job_function.sql" in migrations


def test_make_migration(disk_migrations):
    disk_migrations = {"0001_baseline": disk_migrations["0001_baseline"]}
    filename = "delta_0.8.1_001_add_queueing_lock_column.sql"
    migration = makemigrations.make_migration(
        disk_migrations=disk_migrations,
        missing_migrations=[
            makemigrations.ProcrastinateMigration(
                filename=filename,
                name="add_queueing_lock_column",
                version=(0, 8, 1),
                index=1,
            ),
        ],
    )
    assert migration.name == "0002_add_queueing_lock_column"
    assert migration.dependencies == [("procrastinate", "0001_baseline")]
    assert migration.initial is False
    assert len(migration.operations) == 1
    assert migration.operations[0].filename == filename


def test_make_migration_initial(disk_migrations):
    disk_migrations = {}
    filename = "baseline-0.5.0.sql"
    migration = makemigrations.make_migration(
        disk_migrations=disk_migrations,
        missing_migrations=[
            makemigrations.ProcrastinateMigration(
                filename=filename,
                name="baseline",
                version=(0, 5, 0),
                index=0,
            ),
        ],
    )
    assert migration.name == "0001_baseline"
    assert migration.dependencies == []
    assert migration.initial is True
    assert len(migration.operations) == 1
    assert migration.operations[0].filename == filename


def test_get_missing_migration_no_migration(mocker, disk_migrations):
    mocker.patch(
        "procrastinate.contrib.django.management.commands.makemigrations"
        ".get_all_migrations",
        return_value=[],
    )
    assert makemigrations.get_missing_migration(disk_migrations=disk_migrations) is None
