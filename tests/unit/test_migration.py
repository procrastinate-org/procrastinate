from collections import defaultdict

from procrastinate import sql


def test_get_schema(app):
    assert app.schema_manager.get_schema().startswith("-- Schema version ")


def test_apply_schema(app, connector):
    connector.reverse_queries = defaultdict(lambda: "apply_schema")
    connector.reverse_queries[sql.queries["set_schema_version"]] = "set_schema_version"
    connector.set_schema_version_run = lambda *a, **kw: None
    app.schema_manager.apply_schema()

    assert connector.queries == [
        ("apply_schema", {}),
        ("set_schema_version", {"version": app.schema_manager.version}),
    ]
