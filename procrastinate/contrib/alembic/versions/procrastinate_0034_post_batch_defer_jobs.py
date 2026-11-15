"""03.02.00 50 post batch defer jobs."""

from __future__ import annotations

from procrastinate.contrib.alembic import migrations_utils

revision = "procrastinate_0034"
down_revision: str | None = "procrastinate_0033"
branch_labels = None
depends_on = None

MIGRATION_FILE = "03.02.00_50_post_batch_defer_jobs.sql"


def upgrade() -> None:
    migrations_utils.run_procrastinate_sql(MIGRATION_FILE)


def downgrade() -> None:
    migrations_utils.irreversible()
