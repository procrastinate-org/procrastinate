from typing import Dict

from procrastinate import connector as connector_module
from procrastinate import jobs, sql, utils


@utils.add_sync_api
class HealthCheckRunner:
    def __init__(self, connector: connector_module.BaseConnector):
        self.connector = connector

    async def check_connection_async(self) -> bool:
        result = await self.connector.execute_query_one_async(
            query=sql.queries["check_connection"],
        )
        return result["check"]

    async def get_status_count_async(self) -> Dict[jobs.Status, int]:
        result = await self.connector.execute_query_all_async(
            query=sql.queries["count_jobs_status"],
        )
        result_dict = {r["status"]: int(r["count"]) for r in result}
        return {status: result_dict.get(status.value, 0) for status in jobs.Status}
