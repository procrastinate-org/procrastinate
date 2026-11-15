"""03.03.00 01 pre priority lock fetch job."""

from __future__ import annotations

from procrastinate.contrib.alembic import migrations_utils

revision = "procrastinate_0035"
down_revision: str | None = "procrastinate_0034"
branch_labels = None
depends_on = None

MIGRATION_FILE = "03.03.00_01_pre_priority_lock_fetch_job.sql"


def upgrade() -> None:
    migrations_utils.run_procrastinate_sql(MIGRATION_FILE)


def downgrade() -> None:
    migrations_utils.irreversible()
