from importlib_resources import read_text

from procrastinate import connector as connector_module
from procrastinate import sql, utils


@utils.add_sync_api
class SchemaManager:
    version = "1.1.0"

    def __init__(self, connector: connector_module.BaseConnector):

        self.connector = connector

    @staticmethod
    def get_schema() -> str:
        return read_text("procrastinate.sql", "schema.sql")

    async def apply_schema_async(self) -> None:
        queries = self.get_schema()
        await self.connector.execute_query(query=queries)
        await self.connector.execute_query(
            query=sql.queries["set_schema_version"], version=self.version,
        )
