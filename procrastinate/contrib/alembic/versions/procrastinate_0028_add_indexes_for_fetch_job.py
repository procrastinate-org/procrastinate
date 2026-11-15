"""02.14.01 01 add indexes for fetch job."""

from __future__ import annotations

from procrastinate.contrib.alembic import migrations_utils

revision = "procrastinate_0028"
down_revision: str | None = "procrastinate_0027"
branch_labels = None
depends_on = None

MIGRATION_FILE = "02.14.01_01_add_indexes_for_fetch_job.sql"


def upgrade() -> None:
    migrations_utils.run_procrastinate_sql(MIGRATION_FILE)


def downgrade() -> None:
    migrations_utils.irreversible()
