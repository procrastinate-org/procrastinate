"""00.12.00 01 add foreign key index."""

from __future__ import annotations

from procrastinate.contrib.alembic import migrations_utils

revision = "procrastinate_0010"
down_revision: str | None = "procrastinate_0009"
branch_labels = None
depends_on = None

MIGRATION_FILE = "00.12.00_01_add_foreign_key_index.sql"


def upgrade() -> None:
    migrations_utils.run_procrastinate_sql(MIGRATION_FILE)


def downgrade() -> None:
    migrations_utils.irreversible()
