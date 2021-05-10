import pathlib
import sys

# https://github.com/pypa/twine/pull/551
if sys.version_info[:2] < (3, 9):  # coverage: exclude
    import importlib_resources
else:  # coverage: exclude
    import importlib.resources as importlib_resources

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
