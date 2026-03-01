from __future__ import annotations

import contextlib
import pathlib
import subprocess

import packaging.version
import psycopg
import pytest
from django.core import management
from django.db import connection
from results.dbdiff import Migration

from procrastinate import psycopg_connector, schema


@pytest.fixture
def run_migrations(db_execute):
    def _(dbname):
        folder = pathlib.Path(__file__).parents[2] / "procrastinate/sql/migrations"
        migrations = sorted(folder.glob("*.sql"))

        for migration in migrations:
            with db_execute(dbname) as execute:
                execute(migration.read_text())

    return _


@pytest.fixture
async def schema_database(db_factory, make_psycopg_connection_params):
    dbname = "procrastinate_schema"
    db_factory(dbname=dbname)

    # apply the current procrastinate schema to the "procrastinate_schema" database
    connector = psycopg_connector.PsycopgConnector(
        **make_psycopg_connection_params(dbname=dbname)
    )
    await connector.open_async()
    schema_manager = schema.SchemaManager(connector=connector)
    await schema_manager.apply_schema_async()
    await connector.close_async()

    return dbname


@pytest.fixture
def migrations_database(db_factory, db_execute):
    dbname = "procrastinate_migrations"
    db_factory(dbname=dbname)

    return dbname


@pytest.fixture
def django_db(db):
    yield db


def test_migration(schema_database, migrations_database, run_migrations):
    # apply the migrations on the migrations_database database
    run_migrations(migrations_database)

    # use results to verify that the databases "schema_database" and
    # "migrations_database" have no differences

    with contextlib.ExitStack() as stack:
        schema_db_conn = stack.enter_context(
            psycopg.connect(f"postgresql:///{schema_database}")
        )
        migrations_db_conn = stack.enter_context(
            psycopg.connect(f"postgresql:///{migrations_database}")
        )
        schema_db_cursor = stack.enter_context(schema_db_conn.cursor())
        migrations_db_cursor = stack.enter_context(migrations_db_conn.cursor())
        m = Migration(migrations_db_cursor, schema_db_cursor)
        m.set_safety(False)
        m.add_all_changes()

    print(m.sql)
    assert not m.statements


def test_django_migrations_run_properly(django_db):
    # At this point, with the db fixture, we have all migrations applied
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM procrastinate_jobs")


def test_no_missing_django_migration(django_db):
    management.call_command("makemigrations", "procrastinate", dry_run=True, check=True)


@pytest.fixture(scope="module")
def latest_version() -> packaging.version.Version:
    try:
        subprocess.check_call(["git", "fetch", "--tags"])
        out = subprocess.check_output(["git", "tag", "--list"], text=True)
    except subprocess.CalledProcessError as exc:
        raise ValueError("Cannot fetch latest tag") from exc

    return max(packaging.version.Version(tag) for tag in out.splitlines())


migration_files = sorted(
    (pathlib.Path(__file__).parents[2] / "procrastinate" / "sql" / "migrations").glob(
        "*.sql"
    )
)


@pytest.fixture(scope="module")
def new_migrations(latest_version) -> set[pathlib.Path]:
    # git diff latest_version..HEAD --name-only --diff-filter=A --no-renames -- procrastinate/sql/migrations

    try:
        out = subprocess.check_output(
            [
                "git",
                "diff",
                f"{latest_version}..HEAD",
                "--name-only",
                "--diff-filter=A",
                "--no-renames",
                "--",
                "procrastinate/sql/migrations",
            ],
            text=True,
            stderr=subprocess.PIPE,
        )
    except subprocess.CalledProcessError as exc:
        raise ValueError(f"Cannot fetch new migrations: {exc.stderr}") from exc

    return {pathlib.Path(path) for path in out.splitlines()}


@pytest.mark.parametrize(
    "migration", [pytest.param(m, id=m.name) for m in migration_files]
)
def test_migration_properly_named(
    migration: pathlib.Path,
    latest_version: packaging.version.Version,
    new_migrations: set[pathlib.Path],
):
    # migration is:
    # pathlib.Path("..." / "03.00.00_01_pre_cancel_notification.sql")

    migration_name_parts = migration.stem.split("_", 3)
    version_str, index_str, *pre_post_name = migration_name_parts

    mig_version = packaging.version.Version(version_str)

    next_minor = packaging.version.Version(
        f"{latest_version.major}.{latest_version.minor + 1}.0"
    )

    if migration.name in {m.name for m in new_migrations}:
        assert mig_version == next_minor, (
            f"New migration {migration.name} should be named with {next_minor} but is {mig_version}"
        )
    else:
        assert mig_version <= latest_version, (
            f"Migration {migration.name} should be named with at most {latest_version} but is {mig_version}"
        )

    # All migrations before 3.0.0 are pre migrations
    if mig_version < packaging.version.Version("3.0.0"):
        pre_post = "pre"
        name = pre_post_name[0]
    else:
        pre_post, name = pre_post_name

    index = int(index_str)
    if pre_post == "pre":
        assert 1 <= index < 50, (
            f"Pre migration {migration.name} should have an index between 1 and 49, but is {index}"
        )
    elif pre_post == "post":
        assert 50 <= index < 100, (
            f"Post migration {migration.name} should have an index of at least 50, but is {index}"
        )
    else:
        assert False, f"Invalid migration name: expecting 'pre' or 'post': {pre_post}"

    assert name == name.lower(), (
        f"Migration {migration.name} should be lower case, but is {name}"
    )
    assert "-" not in name, (
        f"Migration {migration.name} should not contain dashes, but is {name}"
    )
    assert " " not in name, (
        f"Migration {migration.name} should not contain spaces, but is {name}"
    )
