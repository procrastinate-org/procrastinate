import pathlib

from importlib_resources import read_text

from procrastinate import connector as connector_module

migrations_path = pathlib.Path(__file__).parent / "sql" / "migrations"


class SchemaManager:
    def __init__(self, connector: connector_module.BaseConnector):

        self.connector = connector

    @staticmethod
    def get_schema() -> str:
        return read_text("procrastinate.sql", "schema.sql")

    @staticmethod
    def get_migrations_path() -> str:
        return str(migrations_path)

    def apply_schema(self) -> None:
        queries = self.get_schema()
        self.connector.execute_query(query=queries)


def get_sql(migration) -> str:
    return read_text("procrastinate.sql.migrations", migration)
