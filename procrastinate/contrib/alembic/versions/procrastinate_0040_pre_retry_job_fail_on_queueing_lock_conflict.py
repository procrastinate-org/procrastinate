"""03.12.00 02 pre retry job fail on queueing lock conflict."""

from __future__ import annotations

from procrastinate.contrib.alembic import migrations_utils

revision = "procrastinate_0040"
down_revision: str | None = "procrastinate_0039"
branch_labels = None
depends_on = None

MIGRATION_FILE = "03.12.00_02_pre_retry_job_fail_on_queueing_lock_conflict.sql"


def upgrade() -> None:
    migrations_utils.run_procrastinate_sql(MIGRATION_FILE)


def downgrade() -> None:
    migrations_utils.irreversible()
