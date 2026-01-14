from __future__ import annotations

import io
import os
import pathlib
import tempfile
import zipfile

import httpx
import nox  # type: ignore
import nox_uv
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


@nox_uv.session
def current_version_with_post_migration(session: nox.Session):
    session.run("uv", "sync", "--all-extras", external=True)
    session.run("uv", "run", "pytest", *session.posargs, external=True)


@nox_uv.session
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


def get_zip_repo(client: httpx.Client, ref: str) -> zipfile.ZipFile:
    response = client.get(
        f"https://api.github.com/repos/procrastinate-org/procrastinate/zipball/{ref}",
        headers={"Accept": "application/vnd.github+json"},
        follow_redirects=True,
    )
    response.raise_for_status()
    return zipfile.ZipFile(io.BytesIO(response.content))


# TODO: set to None after procrastinate 3.7.0 is released
PIN_PYTHON: str | None = "3.13"


@nox_uv.session(python=PIN_PYTHON)
def stable_version_without_post_migration(session: nox.Session):
    latest_tag = fetch_latest_tag(session)
    pre_migration = get_pre_migration(latest_tag)

    with tempfile.TemporaryDirectory() as temp_dir:
        session.chdir(temp_dir)

        temp_path = pathlib.Path(temp_dir)

        # https://api.github.com/repos/procrastinate-org/procrastinate/contents
        # application/vnd.github.raw+json

        try:
            headers = {"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}"}
        except KeyError:
            headers = {}

        client = httpx.Client(headers=headers)

        zip_repo = get_zip_repo(client=client, ref=str(latest_tag))

        for file in zip_repo.namelist():
            if file.endswith("/"):
                continue
            repo_file = file.split("/", 1)[-1]
            if repo_file.startswith("tests") or repo_file in (
                "pyproject.toml",
                "uv.lock",
            ):
                file_path = temp_path / repo_file
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_bytes(zip_repo.read(name=file))

        session.run(
            "uv",
            "sync",
            "--all-extras",
            "--group",
            "test",
            "--no-install-project",
            external=True,
            env={
                **({"UV_PYTHON": PIN_PYTHON} if PIN_PYTHON else {}),
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
