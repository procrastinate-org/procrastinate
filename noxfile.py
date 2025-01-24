from __future__ import annotations

import os
import pathlib
import shutil
import tempfile

import nox  # type: ignore
import packaging.version


def fetch_latest_tag(session: nox.Session) -> packaging.version.Version:
    if "LATEST_TAG" in os.environ:
        return packaging.version.Version(os.environ["LATEST_TAG"])

    session.run("git", "fetch", "--tags", external=True)
    out = session.run("git", "tag", "--list", external=True, silent=True)
    assert out
    return max(packaging.version.Version(tag) for tag in out.splitlines())


def get_pre_migration(latest_tag: packaging.version.Version) -> str:
    migrations_folder = (
        pathlib.Path(__file__).parent / "procrastinate" / "sql" / "migrations"
    )
    migrations = sorted(migrations_folder.glob("*.sql"))
    pre_migration: pathlib.Path | None = None
    for migration in migrations:
        mig_version = packaging.version.Version(migration.name.split("_")[0])
        if mig_version > latest_tag and "_post_" in migration.name:
            break

        pre_migration = migration

    assert pre_migration is not None
    return pre_migration.name


@nox.session
def current_version_with_post_migration(session: nox.Session):
    session.run("uv", "sync", "--all-extras", external=True)
    session.run("uv", "run", "pytest", *session.posargs, external=True)


@nox.session
def current_version_without_post_migration(session: nox.Session):
    latest_tag = fetch_latest_tag(session)
    pre_migration = get_pre_migration(latest_tag)

    session.run(
        "uv",
        "sync",
        "--all-extras",
        "--group",
        "test",
        external=True,
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )
    session.run(
        "pytest",
        f"--migrate-until={pre_migration}",
        "./tests/acceptance",
        *session.posargs,
        external=True,
    )


@nox.session
def stable_version_without_post_migration(session: nox.Session):
    latest_tag = fetch_latest_tag(session)
    pre_migration = get_pre_migration(latest_tag)

    with tempfile.TemporaryDirectory() as temp_dir:
        session.chdir(temp_dir)

        temp_path = pathlib.Path(temp_dir)
        base_path = pathlib.Path(__file__).parent

        # Install test dependencies and copy tests
        shutil.copytree(base_path / "tests", temp_path / "tests")
        shutil.copy(base_path / "pyproject.toml", temp_path / "pyproject.toml")
        shutil.copy(base_path / "uv.lock", temp_path / "uv.lock")
        session.run(
            "uv",
            "sync",
            "--all-extras",
            "--group",
            "test",
            "--no-install-project",
            external=True,
            env={
                "UV_PROJECT_ENVIRONMENT": session.virtualenv.location,
            },
        )

        # Install latest procrastinate from GitHub
        # During a tag release, we have not yet published the new version to PyPI
        # so we need to install it from GitHub
        session.install(
            f"procrastinate @ git+https://github.com/procrastinate-org/procrastinate.git@{latest_tag}"
        )

        session.run(
            "pytest",
            f"--migrate-until={pre_migration}",
            f"--latest-version={latest_tag}",
            "./tests/acceptance",
            *session.posargs,
            # This is necessary for pytest-django, due to not installing the project
            env={"PYTHONPATH": temp_dir},
        )
