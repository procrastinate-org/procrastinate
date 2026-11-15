"""00.16.00 01 add finish job and retry job functions."""

from __future__ import annotations

from procrastinate.contrib.alembic import migrations_utils

revision = "procrastinate_0013"
down_revision: str | None = "procrastinate_0012"
branch_labels = None
depends_on = None

MIGRATION_FILE = "00.16.00_01_add_finish_job_and_retry_job_functions.sql"


def upgrade() -> None:
    migrations_utils.run_procrastinate_sql(MIGRATION_FILE)


def downgrade() -> None:
    migrations_utils.irreversible()
