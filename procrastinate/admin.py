from procrastinate import connector as connector_module
from procrastinate import sql, utils


@utils.add_sync_api
class Admin:
    def __init__(self, connector: connector_module.BaseConnector):
        self.connector = connector

    async def list_jobs_async(self):
        return [
            dict(row) for row in await self.connector.execute_query_all(
                query=sql.queries["list_jobs"],
            )
        ]

    async def list_queues_async(self):
        return [
            {
                "name": row["name"],
                "nb_jobs": row["nb_jobs"],
                "nb_todo": row["stats"].get("todo", 0),
                "nb_succeeded": row["stats"].get("succeeded", 0),
                "nb_failed": row["stats"].get("failed", 0),
            }
            for row in await self.connector.execute_query_all(
                query=sql.queries["list_queues"],
            )
        ]

    async def list_tasks_async(self):
        return [
            {
                "name": row["name"],
                "nb_jobs": row["nb_jobs"],
                "nb_todo": row["stats"].get("todo", 0),
                "nb_succeeded": row["stats"].get("succeeded", 0),
                "nb_failed": row["stats"].get("failed", 0),
            }
            for row in await self.connector.execute_query_all(
                query=sql.queries["list_tasks"],
            )
        ]
