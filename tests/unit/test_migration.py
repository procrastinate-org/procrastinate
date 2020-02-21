from collections import defaultdict

from procrastinate import sql


def test_get_migration_queries(app):
    assert app.migrator.get_migration_queries().startswith("-- Schema version ")


def test_migrate(app, connector):
    connector.reverse_queries = defaultdict(lambda: "migrate")
    connector.reverse_queries[
        sql.queries["set_migration_version"]
    ] = "set_migration_version"
    connector.set_migration_version_run = lambda *a, **kw: None
    app.migrator.migrate()

    assert connector.queries == [
        ("migrate", {}),
        ("set_migration_version", {"version": app.migrator.version}),
    ]
