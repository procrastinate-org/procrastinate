from __future__ import annotations

from importlib import resources

from alembic import op
from sqlalchemy.engine.interfaces import AdaptedConnection


def read_migration_file(name: str) -> str:
    return (
        resources.files("procrastinate.sql.migrations")
        .joinpath(name)
        .read_text(encoding="utf-8")
    )


def run_procrastinate_sql(name: str) -> None:
    """
    Run a SQL migration file from the procrastinate.sql.migrations package
    """
    sql = read_migration_file(name)
    context = op.get_context()
    with context.autocommit_block():
        if context.as_sql:
            context.impl.static_output(sql)
        else:
            execute_script(sql)


def execute_script(sql: str) -> None:
    # A migration file holds several statements, which asyncpg refuses in a
    # prepared statement: the drivers run them as a script when given no
    # parameters.
    dbapi_connection = op.get_bind().connection.dbapi_connection
    if isinstance(dbapi_connection, AdaptedConnection):
        dbapi_connection.run_async(lambda connection: connection.execute(sql))
        return

    assert dbapi_connection is not None
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute(sql)
    finally:
        cursor.close()


def irreversible() -> None:
    raise NotImplementedError(
        "Procrastinate Alembic revisions wrap irreversible SQL migrations."
    )
