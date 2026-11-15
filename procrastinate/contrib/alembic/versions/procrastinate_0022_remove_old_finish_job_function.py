"""01.00.00 01 remove old finish job function."""

from __future__ import annotations

from procrastinate.contrib.alembic import migrations_utils

revision = "procrastinate_0022"
down_revision: str | None = "procrastinate_0021"
branch_labels = None
depends_on = None

MIGRATION_FILE = "01.00.00_01_remove_old_finish_job_function.sql"


def upgrade() -> None:
    migrations_utils.run_procrastinate_sql(MIGRATION_FILE)


def downgrade() -> None:
    migrations_utils.irreversible()
