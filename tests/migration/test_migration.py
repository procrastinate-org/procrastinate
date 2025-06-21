from __future__ import annotations

import contextlib
import os
import pathlib
import subprocess
import warnings

import packaging.version
import pytest
from django.core import management
from django.db import connection
from sqlalchemy.pool import NullPool
from sqlbag import S

from procrastinate import psycopg_connector, schema

with warnings.catch_warnings(record=True):
    # migra uses schemainspect which uses pkg_resources which is deprecated
    warnings.filterwarnings(
        action="ignore", category=DeprecationWarning, module="pkg_resources"
    )
    warnings.filterwarnings(
        action="ignore", category=DeprecationWarning, module="schemainspect"
    )
    from migra import Migration


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

    # use migra to verify that the databases "schema_database" and "migrations_database"
    # have nos differences

    with contextlib.ExitStack() as stack:
        # we use a NullPool to avoid issues when dropping the databases because
        # of opened database sessions
        schema_db_session = stack.enter_context(
            S(f"postgresql:///{schema_database}", poolclass=NullPool)
        )
        migrations_db_session = stack.enter_context(
            S(f"postgresql:///{migrations_database}", poolclass=NullPool)
        )
        m = Migration(migrations_db_session, schema_db_session)
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
    if latest_tag := os.environ.get("LATEST_TAG"):
        return packaging.version.Version(latest_tag)

    if "CI" in os.environ:
        raise ValueError("Cannot fetch latest tag in CI unless LATEST_TAG is set")

    # If we're not in the CI, we can accept loosing a bit of time to fetch the latest tag
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
    # git diff latest_version..HEAD --name-only --diff-filter=A

    try:
        out = subprocess.check_output(
            [
                "git",
                "diff",
                f"{latest_version}..HEAD",
                "--name-only",
                "--diff-filter=A",
            ],
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        raise ValueError("Cannot fetch new migrations") from exc

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

    if migration in new_migrations:
        assert mig_version == next_minor
    else:
        assert mig_version <= latest_version

    if mig_version < packaging.version.Version("3.0.0"):
        pre_post = "pre"
        name = pre_post_name[0]
    else:
        pre_post, name = pre_post_name

    index = int(index_str)
    if pre_post == "pre":
        assert 1 <= index < 50
    elif pre_post == "post":
        assert 50 <= index
    else:
        assert False, f"Invalid migration name: expecting 'pre' or 'post': {pre_post}"

    assert name == name.lower()
    assert "-" not in name
    assert " " not in name
