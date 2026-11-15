"""00.17.00 03 add checks to finish job."""

from __future__ import annotations

from procrastinate.contrib.alembic import migrations_utils

revision = "procrastinate_0016"
down_revision: str | None = "procrastinate_0015"
branch_labels = None
depends_on = None

MIGRATION_FILE = "00.17.00_03_add_checks_to_finish_job.sql"


def upgrade() -> None:
    migrations_utils.run_procrastinate_sql(MIGRATION_FILE)


def downgrade() -> None:
    migrations_utils.irreversible()
