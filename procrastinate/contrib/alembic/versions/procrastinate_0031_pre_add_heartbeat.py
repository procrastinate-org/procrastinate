"""03.01.00 01 pre add heartbeat."""

from __future__ import annotations

from procrastinate.contrib.alembic import migrations_utils

revision = "procrastinate_0031"
down_revision: str | None = "procrastinate_0030"
branch_labels = None
depends_on = None

MIGRATION_FILE = "03.01.00_01_pre_add_heartbeat.sql"


def upgrade() -> None:
    migrations_utils.run_procrastinate_sql(MIGRATION_FILE)


def downgrade() -> None:
    migrations_utils.irreversible()
