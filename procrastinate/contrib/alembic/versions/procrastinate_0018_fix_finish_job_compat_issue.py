"""00.18.01 01 fix finish job compat issue."""

from __future__ import annotations

from procrastinate.contrib.alembic import migrations_utils

revision = "procrastinate_0018"
down_revision: str | None = "procrastinate_0017"
branch_labels = None
depends_on = None

MIGRATION_FILE = "00.18.01_01_fix_finish_job_compat_issue.sql"


def upgrade() -> None:
    migrations_utils.run_procrastinate_sql(MIGRATION_FILE)


def downgrade() -> None:
    migrations_utils.irreversible()
