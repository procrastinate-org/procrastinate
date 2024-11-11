from __future__ import annotations

import functools
import os
import pathlib
import shutil
from typing import Literal, cast

import packaging.version
import psycopg
import pytest
from typing_extensions import LiteralString

from . import utils


@pytest.fixture
def db(db_create, db_drop):
    dbs_to_drop = []

    async def db_factory(dbname, template=None):
        db_create(dbname=dbname, template=template)
        dbs_to_drop.append(dbname)

    yield db_factory

    for dbname in dbs_to_drop:
        db_drop(dbname=dbname)


async def venv(*packages, location: pathlib.Path) -> dict[str, str]:
    await utils.subprocess("python3", "-m", "venv", location)
    await utils.subprocess(
        location / "bin/pip",
        "install",
        *packages,
        env={"POETRY_DYNAMIC_VERSIONING_BYPASS": "0.0.0"},
    )
    return {"PATH": str(location / "bin")}


def merge_env(env: dict[str, str], other: dict[str, str], /) -> dict[str, str]:
    if "PATH" in env and "PATH" in other:
        other["PATH"] = f"{other['PATH']}:{env['PATH']}"
    return env | other


async def apply_migrations(
    *, include_post: bool, latest_tag: packaging.version.Version
):
    sql_folder = pathlib.Path(__file__).parents[2] / "procrastinate/sql"
    if include_post:
        migrations = [sql_folder / "schema.sql"]
    else:
        base = sql_folder / "migrations"
        migrations = sorted(base.glob("*.sql"))
        for migration in list(migrations):
            mig_version = packaging.version.Version(migration.name.split("_")[0])

            if mig_version > latest_tag and "_post_" in migration.name:
                print(f"Skipping post-migration {migration.name}")
                migrations.remove(migration)

        print("Running migrations: ", "\n".join(f"  - {m.name}" for m in migrations))

    async with await psycopg.AsyncConnection.connect() as conn:
        for migration in migrations:
            sql = cast(LiteralString, migration.read_text())
            await conn.execute(sql)
            await conn.commit()


@pytest.fixture(scope="session")
async def latest_tag() -> packaging.version.Version:
    if "LATEST_TAG" in os.environ:
        return packaging.version.Version(os.environ["LATEST_TAG"])

    await utils.subprocess("git", "fetch", "--tags")
    out, _ = await utils.subprocess("git", "tag", "--list")
    return max(packaging.version.Version(tag) for tag in out.splitlines())


@pytest.fixture
async def prepare_acceptance_test(db, monkeypatch, tmp_path, latest_tag):
    async def _(
        *,
        include_post_migrations: bool,
        lib_version: Literal["current", "stable"],
        additional_env: dict[str, str] | None = None,
        operations,
    ):
        # Setup the database
        db_name = "procrastinate_test"
        await db(db_name)
        monkeypatch.setenv("PGDATABASE", db_name)
        pg_envvars = {k: v for k, v in os.environ.items() if k.startswith("PG")}
        pg_envvars["PGDATABASE"] = db_name

        await apply_migrations(
            include_post=include_post_migrations,
            latest_tag=latest_tag,
        )

        # Copy the acceptance app
        shutil.copy("tests/acceptance2/app.py", tmp_path)
        monkeypatch.chdir(tmp_path)

        # Setup the environment
        log_path = tmp_path / "log.txt"
        env = {
            "PATH": os.environ["PATH"],
            "PYTHONPATH": tmp_path,
            **pg_envvars,
            "PROCRASTINATE_APP": "app.app",
            "TEST_CONNECTOR": "procrastinate.PsycopgConnector",
            "TEST_DESTINATION": log_path,
            **(additional_env or {}),
        }

        # Install procrastinate in a venv
        if lib_version == "stable":
            package = "procrastinate"
        else:
            package = pathlib.Path(__file__).parents[2]
        venv_envvars = await venv(package, location=tmp_path / "venv")
        env = merge_env(env, venv_envvars)

        # Configure the CLI calls
        cli = functools.partial(procrastinate_cli, env=env)

        # Configure the test operations
        return functools.partial(operations, cli=cli, logs_path=log_path)

    return _


async def procrastinate_cli(
    *args: str,
    base_command: list[str] | None = None,
    env: dict[str, str] | None = None,
) -> tuple[str, str]:
    env = env or {}
    base_command = base_command or ["procrastinate"]

    print("called with args:", *base_command, *args)
    print("env:\n", "\n".join(f"  {k}: {v}" for k, v in sorted(env.items())))
    return await utils.subprocess(*base_command, *args, env=env)
