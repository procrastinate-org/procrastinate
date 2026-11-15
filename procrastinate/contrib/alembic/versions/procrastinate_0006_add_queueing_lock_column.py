"""00.08.01 01 add queueing lock column."""

from __future__ import annotations

from procrastinate.contrib.alembic import migrations_utils

revision = "procrastinate_0006"
down_revision: str | None = "procrastinate_0005"
branch_labels = None
depends_on = None

MIGRATION_FILE = "00.08.01_01_add_queueing_lock_column.sql"


def upgrade() -> None:
    migrations_utils.run_procrastinate_sql(MIGRATION_FILE)


def downgrade() -> None:
    migrations_utils.irreversible()
