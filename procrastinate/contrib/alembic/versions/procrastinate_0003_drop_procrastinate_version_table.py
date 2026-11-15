"""00.05.00 03 drop procrastinate version table."""

from __future__ import annotations

from procrastinate.contrib.alembic import migrations_utils

revision = "procrastinate_0003"
down_revision: str | None = "procrastinate_0002"
branch_labels = None
depends_on = None

MIGRATION_FILE = "00.05.00_03_drop_procrastinate_version_table.sql"


def upgrade() -> None:
    migrations_utils.run_procrastinate_sql(MIGRATION_FILE)


def downgrade() -> None:
    migrations_utils.irreversible()
