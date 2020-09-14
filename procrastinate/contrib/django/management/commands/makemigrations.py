import pathlib
import sys
from typing import Dict, Iterable, Optional, Tuple

import attr
from django.core.management.commands import makemigrations
from django.db import migrations
from django.db.migrations.autodetector import MigrationAutodetector
from django.db.migrations.loader import MigrationLoader

from procrastinate.contrib.django import utils

DiskMigrations = Dict[str, migrations.Migration]


class Command(makemigrations.Command):
    def handle(self, *app_labels, **options):
        # To avoid polluting user applications, we're only doing something
        # when explicitely requested.
        if "procrastinate" in app_labels:
            self.make_procrastinate_migrations(options)
            app_labels = list(app_labels)
            app_labels.remove("procrastinate")
        return super().handle(*app_labels, **options)

    def make_procrastinate_migrations(self, options):
        self.verbosity = options["verbosity"]
        self.interactive = options["interactive"]
        self.dry_run = options["dry_run"]
        self.include_header = options["include_header"]

        loader = MigrationLoader(None, ignore_no_migrations=True)
        disk_migrations = extract_disk_migrations(loader=loader)

        new_migration = get_missing_migration(disk_migrations=disk_migrations)
        if not new_migration:
            self.stdout.write("No changes detected in procrastinate")
            return

        changes = {"procrastinate": [new_migration]}

        self.write_migration_files(changes)
        if migrations and options["check_changes"]:
            sys.exit(1)

        return


def extract_disk_migrations(loader: MigrationLoader) -> DiskMigrations:
    return {
        name: migration
        for (app, name), migration in loader.disk_migrations.items()
        if app == "procrastinate"
    }


def get_max_existing_migration(
    disk_migrations: DiskMigrations,
) -> Optional[migrations.Migration]:
    if not disk_migrations:
        return None
    return disk_migrations[max(disk_migrations)]


def get_missing_migration(
    disk_migrations: DiskMigrations,
) -> Optional[migrations.Migration]:
    all_migrations = get_all_migrations()
    existing_migration_filenames = set(
        get_existing_migrations(disk_migrations=disk_migrations)
    )
    # Cannot use a set because we need to keep order.
    missing_migrations = [
        m for m in all_migrations if m.filename not in existing_migration_filenames
    ]
    if not missing_migrations:
        return None

    return make_migration(
        disk_migrations=disk_migrations,
        missing_migrations=missing_migrations,
    )


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
        if path.stem.startswith("baseline"):
            name = "baseline"
            index = "000"
            version_str = path.stem.split("-")[1]
        else:
            _, version_str, index, name = path.stem.split("_", 3)
        return cls(
            filename=path.name,
            name=name,
            version=version_from_string(version_str=version_str),
            index=int(index),
        )


def get_all_migrations() -> Iterable[ProcrastinateMigration]:
    all_files = utils.list_migrations()
    migrations = [ProcrastinateMigration.from_path(path=e) for e in all_files]

    return sorted(migrations, key=lambda x: (x.version, x.index))


def get_existing_migrations(disk_migrations: DiskMigrations) -> Iterable[str]:
    for migration in disk_migrations.values():
        for operation in migration.operations:
            if not isinstance(operation, utils.RunProcrastinateFile):
                continue

            yield operation.filename


def make_migration(
    disk_migrations: DiskMigrations,
    missing_migrations: Iterable[ProcrastinateMigration],
):
    migration_name = "_".join(migration.name for migration in missing_migrations)
    previous_migration = get_max_existing_migration(disk_migrations=disk_migrations)

    class NewMigration(migrations.Migration):
        initial = previous_migration is None
        operations = [
            utils.RunProcrastinateFile(filename=migration.filename)
            for migration in missing_migrations
        ]
        _name = migration_name

    if previous_migration:
        NewMigration.dependencies = [("procrastinate", previous_migration.name)]
        index = MigrationAutodetector.parse_number(previous_migration.name) + 1

    else:
        index = 1

    name = f"{index:04d}_{migration_name}"

    return NewMigration(name, "procrastinate")
