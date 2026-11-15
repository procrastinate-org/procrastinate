"""00.17.00 04 add checks to retry job."""

from __future__ import annotations

from procrastinate.contrib.alembic import migrations_utils

revision = "procrastinate_0017"
down_revision: str | None = "procrastinate_0016"
branch_labels = None
depends_on = None

MIGRATION_FILE = "00.17.00_04_add_checks_to_retry_job.sql"


def upgrade() -> None:
    migrations_utils.run_procrastinate_sql(MIGRATION_FILE)


def downgrade() -> None:
    migrations_utils.irreversible()
