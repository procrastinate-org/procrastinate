from importlib_resources import read_text

from procrastinate import store, utils


@utils.add_sync_api
class Migrator:
    def __init__(self, job_store: store.BaseJobStore):

        self.job_store = job_store

    def get_migration_queries(self) -> str:
        return read_text("procrastinate.sql", "structure.sql")

    async def migrate_async(self) -> None:
        queries = self.get_migration_queries()
        await self.job_store.execute_query(query=queries)
