from __future__ import annotations

from importlib import resources

import sqlalchemy as sa
from alembic import op


def read_migration_file(name: str) -> str:
    return (
        resources.files("procrastinate.sql.migrations")
        .joinpath(name)
        .read_text(encoding="utf-8")
    )


def run_procrastinate_sql(name: str) -> None:
    """
    Run a SQL migration file from the procrastinate.sql.migrations package
    """
    with op.get_context().autocommit_block():
        op.execute(sa.text(read_migration_file(name).replace(":", r"\:")))


def irreversible() -> None:
    raise NotImplementedError(
        "Procrastinate Alembic revisions wrap irreversible SQL migrations."
    )
