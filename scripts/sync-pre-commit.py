#!/usr/bin/env python

# /// script
# dependencies = [
#   "ruamel.yaml",
# ]
# ///
# Usage: uv run scripts/sync-pre-commit.py
# or through pre-commit hook: pre-commit run --all-files sync-pre-commit

from __future__ import annotations

import contextlib
import copy
import pathlib
import subprocess
from collections.abc import Generator
from typing import Any, cast

import ruamel.yaml

PRE_COMMIT_PYPI_MAPPING = {
    "pyright-python": "pyright",
    "ruff": "ruff",
    "doc8": "doc8",
}


@contextlib.contextmanager
def yaml_roundtrip(
    path: pathlib.Path,
) -> Generator[dict[str, Any], None, None]:
    yaml = ruamel.yaml.YAML()
    config = cast("dict[str, Any]", yaml.load(path.read_text()))
    old_config = copy.deepcopy(config)
    yield config
    if config != old_config:
        yaml.indent(mapping=2, sequence=4, offset=2)
        yaml.dump(config, path)


def export_from_uv_lock(group_args):
    base_export_args = [
        "uv",
        "export",
        "--all-extras",
        "--no-hashes",
        "--no-header",
        "--no-emit-project",
        "--no-emit-workspace",
    ]
    packages = (
        subprocess.check_output(
            [*base_export_args, *group_args],
            text=True,
        )
        .strip()
        .split("\n")
    )
    return packages


def main():
    groups_typing = [
        "--group=types",
        "--no-group=release",
        "--no-group=lint_format",
        "--no-group=pg_implem",
        "--no-group=test",
        "--no-group=docs",
    ]
    groups_dev = [
        "--only-group=dev",
    ]
    typing_dependencies = export_from_uv_lock(groups_typing)
    dev_dependencies = export_from_uv_lock(groups_dev)
    dev_versions = dict(e.split("==") for e in dev_dependencies)

    with yaml_roundtrip(pathlib.Path(".pre-commit-config.yaml")) as pre_commit_config:
        for repo in pre_commit_config["repos"]:
            repo_name = repo["repo"].split("/")[-1]
            pypi_package = PRE_COMMIT_PYPI_MAPPING.get(repo_name)
            if pypi_package:
                repo["rev"] = f"v{dev_versions[pypi_package]}"

            if repo_name == "pyright-python":
                repo["hooks"][0]["additional_dependencies"] = typing_dependencies


if __name__ == "__main__":
    main()
