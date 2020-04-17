from procrastinate import connector as connector_module
from procrastinate import sql, utils


@utils.add_sync_api
class Admin:
    def __init__(self, connector: connector_module.BaseConnector):
        self.connector = connector

    async def list_jobs_async(
        self, id=None, queue=None, task=None, status=None, lock=None,
    ):
        return [
            dict(row)
            for row in await self.connector.execute_query_all(
                query=sql.queries["list_jobs"],
                id=id,
                queue=queue,
                task=task,
                status=status,
                lock=lock,
            )
        ]

    async def list_queues_async(
        self, queue=None, task=None, status=None, lock=None,
    ):
        return [
            {
                "name": row["name"],
                "nb_jobs": row["nb_jobs"],
                "nb_todo": row["stats"].get("todo", 0),
                "nb_doing": row["stats"].get("doing", 0),
                "nb_succeeded": row["stats"].get("succeeded", 0),
                "nb_failed": row["stats"].get("failed", 0),
            }
            for row in await self.connector.execute_query_all(
                query=sql.queries["list_queues"],
                queue=queue,
                task=task,
                status=status,
                lock=lock,
            )
        ]

    async def list_tasks_async(
        self, queue=None, task=None, status=None, lock=None,
    ):
        return [
            {
                "name": row["name"],
                "nb_jobs": row["nb_jobs"],
                "nb_todo": row["stats"].get("todo", 0),
                "nb_doing": row["stats"].get("doing", 0),
                "nb_succeeded": row["stats"].get("succeeded", 0),
                "nb_failed": row["stats"].get("failed", 0),
            }
            for row in await self.connector.execute_query_all(
                query=sql.queries["list_tasks"],
                queue=queue,
                task=task,
                status=status,
                lock=lock,
            )
        ]

    async def set_job_status_async(self, id, status):
        await self.connector.execute_query(
            query=sql.queries["set_job_status"], id=id, status=status,
        )
        (result,) = await self.list_jobs_async(id=id)
        return result
