"""02.08.00 01 add additional params to retry job."""

from __future__ import annotations

from procrastinate.contrib.alembic import migrations_utils

revision = "procrastinate_0027"
down_revision: str | None = "procrastinate_0026"
branch_labels = None
depends_on = None

MIGRATION_FILE = "02.08.00_01_add_additional_params_to_retry_job.sql"


def upgrade() -> None:
    migrations_utils.run_procrastinate_sql(MIGRATION_FILE)


def downgrade() -> None:
    migrations_utils.irreversible()
