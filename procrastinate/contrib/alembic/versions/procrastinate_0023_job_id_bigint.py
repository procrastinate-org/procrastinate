"""01.01.01 01 job id bigint."""

from __future__ import annotations

from procrastinate.contrib.alembic import migrations_utils

revision = "procrastinate_0023"
down_revision: str | None = "procrastinate_0022"
branch_labels = None
depends_on = None

MIGRATION_FILE = "01.01.01_01_job_id_bigint.sql"


def upgrade() -> None:
    migrations_utils.run_procrastinate_sql(MIGRATION_FILE)


def downgrade() -> None:
    migrations_utils.irreversible()
