from collections import defaultdict


def test_get_migration_queries(app):
    assert app.migrator.get_migration_queries().startswith("CREATE")


def test_migrate(app, job_store):
    job_store.reverse_queries = defaultdict(lambda: "migrate")
    app.migrator.migrate()

    assert app.job_store.queries == [("migrate", {})]
