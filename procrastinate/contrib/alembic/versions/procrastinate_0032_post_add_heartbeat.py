"""03.01.00 50 post add heartbeat."""

from __future__ import annotations

from procrastinate.contrib.alembic import migrations_utils

revision = "procrastinate_0032"
down_revision: str | None = "procrastinate_0031"
branch_labels = None
depends_on = None

MIGRATION_FILE = "03.01.00_50_post_add_heartbeat.sql"


def upgrade() -> None:
    migrations_utils.run_procrastinate_sql(MIGRATION_FILE)


def downgrade() -> None:
    migrations_utils.irreversible()
