from procrastinate import store, sql, utils
from procrastinate.migration import Migrator

@utils.add_sync_api
class HealthCheckRunner:
    def __init__(self, job_store: store.BaseJobStore):
        self.job_store = job_store

    async def check_connection_async(self):
        result = await self.job_store.execute_query_one(
            query=sql.queries['check_connection'],
        )
        return result['check']

    async def check_db_version_async(self):
        result = await self.job_store.execute_query_one(
            query=sql.queries['get_latest_version'],
        )
        return result['version'] == Migrator.version
