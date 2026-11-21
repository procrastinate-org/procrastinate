"""03.13.00 50 post drop retry job v2."""

from __future__ import annotations

from procrastinate.contrib.alembic import migrations_utils

revision = "procrastinate_0045"
down_revision: str | None = "procrastinate_0044"
branch_labels = None
depends_on = None

MIGRATION_FILE = "03.13.00_50_post_drop_retry_job_v2.sql"


def upgrade() -> None:
    migrations_utils.run_procrastinate_sql(MIGRATION_FILE)


def downgrade() -> None:
    migrations_utils.irreversible()
