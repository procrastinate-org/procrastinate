from __future__ import annotations

import pathlib
from collections import defaultdict


def test_get_schema(app):
    assert app.schema_manager.get_schema().startswith("-- Procrastinate Schema")


def test_get_migrations_path(app):
    assert app.schema_manager.get_migrations_path().endswith("sql/migrations")


def test_get_alembic_versions_path(app):
    path = pathlib.Path(app.schema_manager.get_alembic_versions_path())

    assert path.name == "versions"
    assert path.parent.name == "alembic"


def test_get_alembic_config_snippet(app):
    snippet = app.schema_manager.get_alembic_config_snippet()

    assert "version_locations = %(here)s/versions" in snippet
    assert app.schema_manager.get_alembic_versions_path() in snippet


def test_apply_schema(app, connector):
    connector.reverse_queries = defaultdict(lambda: "apply_schema")
    connector.set_schema_version_run = lambda *a, **kw: None
    app.schema_manager.apply_schema()

    assert connector.queries == [("apply_schema", {})]


async def test_apply_schema_async(app, connector):
    connector.reverse_queries = defaultdict(lambda: "apply_schema")
    connector.set_schema_version_run = lambda *a, **kw: None
    await app.schema_manager.apply_schema_async()

    assert connector.queries == [("apply_schema", {})]
