def test_get_migration_queries(app):
    assert app.migrator.get_migration_queries().startswith("CREATE")


def test_migrate(app):
    app.migrator.migrate()

    assert len(app.job_store.queries)
