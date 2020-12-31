import pathlib

import importlib_resources

from procrastinate import connector as connector_module

migrations_path = pathlib.Path(__file__).parent / "sql" / "migrations"


class SchemaManager:
    def __init__(self, connector: connector_module.BaseConnector):

        self.connector = connector

    @staticmethod
    def get_schema() -> str:
        return importlib_resources.read_text("procrastinate.sql", "schema.sql")

    @staticmethod
    def get_migrations_path() -> str:
        return str(migrations_path)

    def apply_schema(self) -> None:
        queries = self.get_schema()
        self.connector.execute_query(query=queries)

    async def apply_schema_async(self) -> None:
        queries = self.get_schema()
        await self.connector.execute_query_async(query=queries)
