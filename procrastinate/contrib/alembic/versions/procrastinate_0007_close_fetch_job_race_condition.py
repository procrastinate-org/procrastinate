"""00.10.00 01 close fetch job race condition."""

from __future__ import annotations

from procrastinate.contrib.alembic import migrations_utils

revision = "procrastinate_0007"
down_revision: str | None = "procrastinate_0006"
branch_labels = None
depends_on = None

MIGRATION_FILE = "00.10.00_01_close_fetch_job_race_condition.sql"


def upgrade() -> None:
    migrations_utils.run_procrastinate_sql(MIGRATION_FILE)


def downgrade() -> None:
    migrations_utils.irreversible()
