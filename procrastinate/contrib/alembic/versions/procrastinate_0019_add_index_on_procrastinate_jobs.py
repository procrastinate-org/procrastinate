"""00.19.00 01 add index on procrastinate jobs."""

from __future__ import annotations

from procrastinate.contrib.alembic import migrations_utils

revision = "procrastinate_0019"
down_revision: str | None = "procrastinate_0018"
branch_labels = None
depends_on = None

MIGRATION_FILE = "00.19.00_01_add_index_on_procrastinate_jobs.sql"


def upgrade() -> None:
    migrations_utils.run_procrastinate_sql(MIGRATION_FILE)


def downgrade() -> None:
    migrations_utils.irreversible()
