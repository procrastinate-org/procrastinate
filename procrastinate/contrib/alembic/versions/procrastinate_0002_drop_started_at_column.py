"""00.05.00 02 drop started at column."""

from __future__ import annotations

from procrastinate.contrib.alembic import migrations_utils

revision = "procrastinate_0002"
down_revision: str | None = "procrastinate_0001"
branch_labels = None
depends_on = None

MIGRATION_FILE = "00.05.00_02_drop_started_at_column.sql"


def upgrade() -> None:
    migrations_utils.run_procrastinate_sql(MIGRATION_FILE)


def downgrade() -> None:
    migrations_utils.irreversible()
