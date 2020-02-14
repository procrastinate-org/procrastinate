from importlib_resources import read_text

from procrastinate import connector as connector_module
from procrastinate import sql, utils


@utils.add_sync_api
class Migrator:
    version = "0.2.1"

    def __init__(self, connector: connector_module.BaseConnector):

        self.connector = connector

    def get_migration_queries(self) -> str:
        return read_text("procrastinate.sql", "structure.sql")

    async def migrate_async(self) -> None:
        queries = self.get_migration_queries()
        await self.connector.execute_query(query=queries)
        await self.connector.execute_query(
            query=sql.queries["set_migration_version"], version=Migrator.version,
        )
