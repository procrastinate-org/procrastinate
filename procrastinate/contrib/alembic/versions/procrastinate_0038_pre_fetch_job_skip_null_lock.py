"""03.11.00 01 pre fetch job skip null lock."""

from __future__ import annotations

from procrastinate.contrib.alembic import migrations_utils

revision = "procrastinate_0038"
down_revision: str | None = "procrastinate_0037"
branch_labels = None
depends_on = None

MIGRATION_FILE = "03.11.00_01_pre_fetch_job_skip_null_lock.sql"


def upgrade() -> None:
    migrations_utils.run_procrastinate_sql(MIGRATION_FILE)


def downgrade() -> None:
    migrations_utils.irreversible()
