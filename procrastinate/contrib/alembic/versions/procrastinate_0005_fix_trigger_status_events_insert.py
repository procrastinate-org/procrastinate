"""00.07.01 01 fix trigger status events insert."""

from __future__ import annotations

from procrastinate.contrib.alembic import migrations_utils

revision = "procrastinate_0005"
down_revision: str | None = "procrastinate_0004"
branch_labels = None
depends_on = None

MIGRATION_FILE = "00.07.01_01_fix_trigger_status_events_insert.sql"


def upgrade() -> None:
    migrations_utils.run_procrastinate_sql(MIGRATION_FILE)


def downgrade() -> None:
    migrations_utils.irreversible()
