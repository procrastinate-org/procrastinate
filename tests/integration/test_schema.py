from __future__ import annotations

from procrastinate import App, PsycopgConnector


def test_apply_schema(db_factory, monkeypatch):
    monkeypatch.setenv("PGDATABASE", "procrastinate_test")
    db_factory(dbname="procrastinate_test")
    app = App(connector=PsycopgConnector())

    with app.open():
        app.schema_manager.apply_schema()


async def test_apply_schema_async(db_factory, monkeypatch):
    monkeypatch.setenv("PGDATABASE", "procrastinate_test")
    db_factory(dbname="procrastinate_test")
    app = App(connector=PsycopgConnector())

    async with app.open_async():
        await app.schema_manager.apply_schema_async()
