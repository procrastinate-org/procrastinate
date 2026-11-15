"""00.00.00 01 initial."""

from __future__ import annotations

from procrastinate.contrib.alembic import migrations_utils

revision = "procrastinate_0000"
down_revision: str | None = None
branch_labels = ("procrastinate",)
depends_on = None

MIGRATION_FILE = "00.00.00_01_initial.sql"


def upgrade() -> None:
    migrations_utils.run_procrastinate_sql(MIGRATION_FILE)


def downgrade() -> None:
    migrations_utils.irreversible()
