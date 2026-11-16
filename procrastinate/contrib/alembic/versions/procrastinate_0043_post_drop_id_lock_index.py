"""03.12.00 51 post drop id lock index."""

from __future__ import annotations

from procrastinate.contrib.alembic import migrations_utils

revision = "procrastinate_0043"
down_revision: str | None = "procrastinate_0042"
branch_labels = None
depends_on = None

MIGRATION_FILE = "03.12.00_51_post_drop_id_lock_index.sql"


def upgrade() -> None:
    migrations_utils.run_procrastinate_sql(MIGRATION_FILE)


def downgrade() -> None:
    migrations_utils.irreversible()
