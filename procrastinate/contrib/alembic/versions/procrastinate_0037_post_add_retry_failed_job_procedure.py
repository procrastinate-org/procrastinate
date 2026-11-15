"""03.04.00 50 post add retry failed job procedure."""

from __future__ import annotations

from procrastinate.contrib.alembic import migrations_utils

revision = "procrastinate_0037"
down_revision: str | None = "procrastinate_0036"
branch_labels = None
depends_on = None

MIGRATION_FILE = "03.04.00_50_post_add_retry_failed_job_procedure.sql"


def upgrade() -> None:
    migrations_utils.run_procrastinate_sql(MIGRATION_FILE)


def downgrade() -> None:
    migrations_utils.irreversible()
