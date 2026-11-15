"""02.05.00 01 add periodic job priority."""

from __future__ import annotations

from procrastinate.contrib.alembic import migrations_utils

revision = "procrastinate_0025"
down_revision: str | None = "procrastinate_0024"
branch_labels = None
depends_on = None

MIGRATION_FILE = "02.05.00_01_add_periodic_job_priority.sql"


def upgrade() -> None:
    migrations_utils.run_procrastinate_sql(MIGRATION_FILE)


def downgrade() -> None:
    migrations_utils.irreversible()
