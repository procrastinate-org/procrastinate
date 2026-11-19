"""03.12.00 03 pre add todo doing lock index."""

from __future__ import annotations

from procrastinate.contrib.alembic import migrations_utils

revision = "procrastinate_0041"
down_revision: str | None = "procrastinate_0040"
branch_labels = None
depends_on = None

MIGRATION_FILE = "03.12.00_03_pre_add_todo_doing_lock_index.sql"


def upgrade() -> None:
    migrations_utils.run_procrastinate_sql(MIGRATION_FILE)


def downgrade() -> None:
    migrations_utils.irreversible()
