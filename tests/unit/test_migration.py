from collections import defaultdict

from procrastinate import sql


def test_get_migration_queries(app):
    assert app.migrator.get_migration_queries().startswith("CREATE")


def test_migrate(app, job_store):
    job_store.reverse_queries = defaultdict(lambda: "migrate")
    job_store.reverse_queries[
        sql.queries["set_migration_version"]
    ] = "set_migration_version"
    job_store.set_migration_version_run = lambda *a, **kw: None
    app.migrator.migrate()

    assert app.job_store.queries == [
        ("migrate", {}),
        ("set_migration_version", {"version": app.migrator.version}),
    ]
