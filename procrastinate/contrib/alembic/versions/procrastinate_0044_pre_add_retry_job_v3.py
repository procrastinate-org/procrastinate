"""03.13.00 01 pre add retry job v3."""

from __future__ import annotations

from procrastinate.contrib.alembic import migrations_utils

revision = "procrastinate_0044"
down_revision: str | None = "procrastinate_0043"
branch_labels = None
depends_on = None

MIGRATION_FILE = "03.13.00_01_pre_add_retry_job_v3.sql"


def upgrade() -> None:
    migrations_utils.run_procrastinate_sql(MIGRATION_FILE)


def downgrade() -> None:
    migrations_utils.irreversible()
