import pathlib
from collections import defaultdict

from procrastinate.schema import SchemaManager


def test_get_schema(app):
    assert app.schema_manager.get_schema().startswith("-- Schema version ")


def test_get_version(mocker):
    mock = mocker.patch("pathlib.Path.glob")
    mock.return_value = [
        pathlib.Path("/foo/bar/delta_1.0.8_test.sql"),
        pathlib.Path("/foo/bar/delta_1.0.9_test.sql"),
        pathlib.Path("/foo/bar/delta_1.0.10_test.sql"),
    ]
    assert SchemaManager.get_version() == "1.0.10"


def test_apply_schema(app, connector):
    connector.reverse_queries = defaultdict(lambda: "apply_schema")
    connector.set_schema_version_run = lambda *a, **kw: None
    app.schema_manager.apply_schema()

    assert connector.queries == [("apply_schema", {})]
