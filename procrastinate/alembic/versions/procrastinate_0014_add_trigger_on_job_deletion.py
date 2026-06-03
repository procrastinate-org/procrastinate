"""00.17.00 01 add trigger on job deletion."""

from __future__ import annotations

from importlib import resources

import sqlalchemy as sa
from alembic import op

revision = "procrastinate_0014"
down_revision = 'procrastinate_0013'
branch_labels = ("procrastinate",) if down_revision is None else None
depends_on = None

MIGRATION_FILE = "00.17.00_01_add_trigger_on_job_deletion.sql"


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
