"""02.06.00 01 add cancel states."""

from __future__ import annotations

from procrastinate.contrib.alembic import migrations_utils

revision = "procrastinate_0026"
down_revision: str | None = "procrastinate_0025"
branch_labels = None
depends_on = None

MIGRATION_FILE = "02.06.00_01_add_cancel_states.sql"


def upgrade() -> None:
    migrations_utils.run_procrastinate_sql(MIGRATION_FILE)


def downgrade() -> None:
    migrations_utils.irreversible()
