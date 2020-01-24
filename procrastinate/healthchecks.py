from typing import Tuple

from psycopg2 import Error
from procrastinate import store, sql, utils
from procrastinate.migration import Migrator

@utils.add_sync_api
class HealthCheckRunner:
    def __init__(self, job_store: store.BaseJobStore):
        self.job_store = job_store

    async def check_connection_async(self) -> Tuple[bool, str]:
        try:
            result = await self.job_store.execute_query_one(
                query=sql.queries['check_connection'],
            )
            return result['check'], "OK"
        except Error as e:
            return False, str(e)

    async def check_db_version_async(self) -> Tuple[bool, str]:
        try:
            result = await self.job_store.execute_query_one(
                query=sql.queries['get_latest_version'],
            )
            return result['version'] == Migrator.version, "OK"
        except Error as e:
            return False, str(e)
