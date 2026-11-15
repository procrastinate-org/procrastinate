"""00.17.00 01 add trigger on job deletion."""

from __future__ import annotations

from procrastinate.contrib.alembic import migrations_utils

revision = "procrastinate_0014"
down_revision: str | None = "procrastinate_0013"
branch_labels = None
depends_on = None

MIGRATION_FILE = "00.17.00_01_add_trigger_on_job_deletion.sql"


def upgrade() -> None:
    migrations_utils.run_procrastinate_sql(MIGRATION_FILE)


def downgrade() -> None:
    migrations_utils.irreversible()
