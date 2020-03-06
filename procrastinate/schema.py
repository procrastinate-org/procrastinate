import pathlib

from importlib_resources import read_text

from procrastinate import connector as connector_module
from procrastinate import utils

migrations_path = pathlib.Path(__file__).parent / "sql" / "migrations"


@utils.add_sync_api
class SchemaManager:
    def __init__(self, connector: connector_module.BaseConnector):

        self.connector = connector

    @staticmethod
    def get_schema() -> str:
        return read_text("procrastinate.sql", "schema.sql")

    @staticmethod
    def get_migrations_path() -> str:
        return str(migrations_path)

    async def apply_schema_async(self) -> None:
        queries = self.get_schema()
        await self.connector.execute_query(query=queries)
