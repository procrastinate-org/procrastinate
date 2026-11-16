"""03.12.00 50 post add lock mode."""

from __future__ import annotations

from procrastinate.contrib.alembic import migrations_utils

revision = "procrastinate_0042"
down_revision: str | None = "procrastinate_0041"
branch_labels = None
depends_on = None

MIGRATION_FILE = "03.12.00_50_post_add_lock_mode.sql"


def upgrade() -> None:
    migrations_utils.run_procrastinate_sql(MIGRATION_FILE)


def downgrade() -> None:
    migrations_utils.irreversible()
