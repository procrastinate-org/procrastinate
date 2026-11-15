"""00.11.00 03 add procrastinate periodic defers."""

from __future__ import annotations

from procrastinate.contrib.alembic import migrations_utils

revision = "procrastinate_0009"
down_revision: str | None = "procrastinate_0008"
branch_labels = None
depends_on = None

MIGRATION_FILE = "00.11.00_03_add_procrastinate_periodic_defers.sql"


def upgrade() -> None:
    migrations_utils.run_procrastinate_sql(MIGRATION_FILE)


def downgrade() -> None:
    migrations_utils.irreversible()
