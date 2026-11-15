"""03.00.00 50 post cancel notification."""

from __future__ import annotations

from procrastinate.contrib.alembic import migrations_utils

revision = "procrastinate_0030"
down_revision: str | None = "procrastinate_0029"
branch_labels = None
depends_on = None

MIGRATION_FILE = "03.00.00_50_post_cancel_notification.sql"


def upgrade() -> None:
    migrations_utils.run_procrastinate_sql(MIGRATION_FILE)


def downgrade() -> None:
    migrations_utils.irreversible()
