"""00.17.00 02 delete finished jobs."""

from __future__ import annotations

from procrastinate.contrib.alembic import migrations_utils

revision = "procrastinate_0015"
down_revision: str | None = "procrastinate_0014"
branch_labels = None
depends_on = None

MIGRATION_FILE = "00.17.00_02_delete_finished_jobs.sql"


def upgrade() -> None:
    migrations_utils.run_procrastinate_sql(MIGRATION_FILE)


def downgrade() -> None:
    migrations_utils.irreversible()
