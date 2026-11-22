#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml"]
# ///
"""
Keep the supported Python and PostgreSQL versions consistent across the repo.

- Python: `requires-python` in pyproject.toml is the source of truth. The README is
  rewritten from it, and the CI test matrix must test every minor version from it on.
- PostgreSQL: the oldest version in the CI test matrix is the source of truth. The
  README is rewritten from it. The matrix must test every version from it on, up to
  the one the other CI jobs use (kept up to date by Renovate).
"""

from __future__ import annotations

import pathlib
import re
import sys
import tomllib

import yaml

ROOT = pathlib.Path(__file__).parents[1]
README = ROOT / "README.md"
PYPROJECT = ROOT / "pyproject.toml"
CI = ROOT / ".github" / "workflows" / "ci.yml"


def rewrite(path: pathlib.Path, pattern: str, replacement: str) -> None:
    text = path.read_text()
    new, count = re.subn(pattern, replacement, text)
    if count != 1:
        sys.exit(f"{path.name}: expected exactly one match for {pattern!r}")
    if new != text:
        path.write_text(new)
        print(f"{path.name}: updated to {replacement!r}")


def main() -> int:
    requires_python = tomllib.loads(PYPROJECT.read_text())["project"]["requires-python"]
    match = re.fullmatch(r">=3\.(\d+)(?:\.\d+)?", requires_python)
    if not match:
        sys.exit(f"pyproject.toml: unexpected requires-python {requires_python!r}")
    python_minor = int(match.group(1))

    jobs = yaml.safe_load(CI.read_text())["jobs"]
    matrix = jobs["tests"]["strategy"]["matrix"]["include"]
    ci_python = {int(row["python-version"].removeprefix("3.")) for row in matrix}
    ci_postgres = {int(row["postgres-version"]) for row in matrix}
    other_images = {
        job["services"]["postgres"]["image"]
        for name, job in jobs.items()
        if name != "tests" and "postgres" in job.get("services", {})
    }

    rewrite(
        README,
        r'<span id="min-python">[^<]*</span>',
        f'<span id="min-python">3.{python_minor}</span>',
    )
    rewrite(
        README,
        r'<span id="min-postgres">[^<]*</span>',
        f'<span id="min-postgres">{min(ci_postgres)}</span>',
    )

    errors = [
        f"CI test matrix doesn't test Python 3.{minor}"
        for minor in range(python_minor, max(ci_python) + 1)
        if minor not in ci_python
    ]
    errors += [
        f"CI test matrix doesn't test PostgreSQL {version}"
        for version in range(min(ci_postgres), max(ci_postgres) + 1)
        if version not in ci_postgres
    ]
    if min(ci_python) < python_minor:
        errors.append(
            f"CI test matrix tests Python 3.{min(ci_python)}, "
            f"older than requires-python {requires_python}"
        )
    if other_images != {f"postgres:{max(ci_postgres)}"}:
        errors.append(
            f"CI test matrix's newest PostgreSQL is {max(ci_postgres)}, "
            f"but other jobs use {', '.join(sorted(other_images))}"
        )
    for error in errors:
        print(error, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
