from typing import Dict, Tuple

from psycopg2 import Error

from procrastinate import jobs, sql, store, utils
from procrastinate.migration import Migrator


@utils.add_sync_api
class HealthCheckRunner:
    def __init__(self, job_store: store.BaseJobStore):
        self.job_store = job_store

    async def check_connection_async(self) -> Tuple[bool, str]:
        try:
            result = await self.job_store.execute_query_one(
                query=sql.queries["check_connection"],
            )
            return result["check"], "OK"
        except Error as e:
            return False, str(e)

    async def check_db_version_async(self) -> Tuple[bool, str]:
        try:
            result = await self.job_store.execute_query_one(
                query=sql.queries["get_latest_version"],
            )
            return result["version"] == Migrator.version, "OK"
        except Error as e:
            return False, str(e)

    async def get_status_count_async(self) -> Dict[jobs.Status, int]:
        result = await self.job_store.execute_query_all(
            query=sql.queries["count_jobs_status"],
        )
        result_dict = {r["status"]: int(r["count"]) for r in result}
        return {status: result_dict.get(status.value, 0) for status in jobs.Status}
