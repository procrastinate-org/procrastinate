from collections import defaultdict


def test_get_schema(app):
    assert app.schema_manager.get_schema().startswith("-- Schema version ")


def test_apply_schema(app, connector):
    connector.reverse_queries = defaultdict(lambda: "apply_schema")
    connector.set_schema_version_run = lambda *a, **kw: None
    app.schema_manager.apply_schema()

    assert connector.queries == [("apply_schema", {})]
