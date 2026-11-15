"""00.15.02 01 fix procrastinate defer periodic job."""

from __future__ import annotations

from procrastinate.contrib.alembic import migrations_utils

revision = "procrastinate_0012"
down_revision: str | None = "procrastinate_0011"
branch_labels = None
depends_on = None

MIGRATION_FILE = "00.15.02_01_fix_procrastinate_defer_periodic_job.sql"


def upgrade() -> None:
    migrations_utils.run_procrastinate_sql(MIGRATION_FILE)


def downgrade() -> None:
    migrations_utils.irreversible()
