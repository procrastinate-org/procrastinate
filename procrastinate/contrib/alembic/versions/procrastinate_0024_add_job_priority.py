"""02.00.03 01 add job priority."""

from __future__ import annotations

from procrastinate.contrib.alembic import migrations_utils

revision = "procrastinate_0024"
down_revision: str | None = "procrastinate_0023"
branch_labels = None
depends_on = None

MIGRATION_FILE = "02.00.03_01_add_job_priority.sql"


def upgrade() -> None:
    migrations_utils.run_procrastinate_sql(MIGRATION_FILE)


def downgrade() -> None:
    migrations_utils.irreversible()
