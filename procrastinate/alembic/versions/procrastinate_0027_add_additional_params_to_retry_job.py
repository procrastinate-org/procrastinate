"""02.08.00 01 add additional params to retry job."""

from __future__ import annotations

from importlib import resources

import sqlalchemy as sa
from alembic import op

revision = "procrastinate_0027"
down_revision = 'procrastinate_0026'
branch_labels = ("procrastinate",) if down_revision is None else None
depends_on = None

MIGRATION_FILE = "02.08.00_01_add_additional_params_to_retry_job.sql"


def _migration_sql() -> sa.TextClause:
    sql = (
        resources.files("procrastinate.sql.migrations")
        .joinpath(MIGRATION_FILE)
        .read_text(encoding="utf-8")
    )
    return sa.text(sql.replace(":", r"\:"))


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute(_migration_sql())


def downgrade() -> None:
    raise NotImplementedError(
        "Procrastinate Alembic revisions wrap irreversible SQL migrations."
    )
