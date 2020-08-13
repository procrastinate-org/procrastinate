from collections import defaultdict

from procrastinate import schema


def test_get_schema(app):
    assert app.schema_manager.get_schema().startswith("-- Procrastinate Schema")


def test_get_migrations_path(app):
    assert app.schema_manager.get_migrations_path().endswith("sql/migrations")


def test_apply_schema(app, connector):
    connector.reverse_queries = defaultdict(lambda: "apply_schema")
    connector.set_schema_version_run = lambda *a, **kw: None
    app.schema_manager.apply_schema()

    assert connector.queries == [("apply_schema", {})]


def test_get_sql(app):
    migration_name = "baseline-0.5.0.sql"
    migration = schema.get_sql(migration_name)

    assert migration.startswith(
        "CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;"
    )
    assert len(migration.splitlines()) == 187
