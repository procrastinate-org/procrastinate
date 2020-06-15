from typing import Any, Dict, Iterable, Optional

from procrastinate import connector as connector_module
from procrastinate import sql, utils


@utils.add_sync_api
class Admin:
    """
    The Admin is used to overview and administrate procrastinate jobs.

    You should never need to instantiate an Admin object as it is
    already available as `App.admin`.
    """

    def __init__(self, connector: connector_module.BaseConnector):
        """
        Parameters
        ----------
        connector :
            Instance of a subclass of :py:class:`procrastinate.connector.BaseConnector`,
            typically `AiopgConnector`. It will be responsible for all communications
            with the database. Mandatory.
        """
        self.connector = connector

    async def list_jobs_async(
        self,
        id: Optional[int] = None,
        queue: Optional[str] = None,
        task: Optional[str] = None,
        status: Optional[str] = None,
        lock: Optional[str] = None,
        queueing_lock: Optional[str] = None,
    ) -> Iterable[Dict[str, Any]]:
        """
        List all procrastinate jobs given query filters.

        Parameters
        ----------
        id : ``int``
            Filter by job ID
        queue : ``str``
            Filter by job queue name
        task : ``str``
            Filter by job task name
        status : ``str``
            Filter by job status (*todo*/*doing*/*succeeded*/*failed*)
        lock : ``str``
            Filter by job lock
        queueing_lock : ``str``
            Filter by job queueing_lock

        Returns
        -------
        ``List[Dict[str, Any]]``
            A list of dictionaries representing jobs (``id``, ``queue``, ``task``,
            ``lock``, ``args``, ``status``, ``scheduled_at``, ``attempts``).
        """
        return [
            {
                "id": row["id"],
                "queue": row["queue_name"],
                "task": row["task_name"],
                "lock": row["lock"],
                "queueing_lock": row["queueing_lock"],
                "args": row["args"],
                "status": row["status"],
                "scheduled_at": row["scheduled_at"],
                "attempts": row["attempts"],
            }
            for row in await self.connector.execute_query_all_async(
                query=sql.queries["list_jobs"],
                id=id,
                queue_name=queue,
                task_name=task,
                status=status,
                lock=lock,
                queueing_lock=queueing_lock,
            )
        ]

    async def list_queues_async(
        self,
        queue: Optional[str] = None,
        task: Optional[str] = None,
        status: Optional[str] = None,
        lock: Optional[str] = None,
    ) -> Iterable[Dict[str, Any]]:
        """
        List all queues and number of jobs per status for each queue.

        Parameters
        ----------
        queue : ``str``
            Filter by job queue name
        task : ``str``
            Filter by job task name
        status : ``str``
            Filter by job status (*todo*/*doing*/*succeeded*/*failed*)
        lock : ``str``
            Filter by job lock

        Returns
        -------
        ``List[Dict[str, Any]]``
            A list of dictionaries representing queues stats (``name``, ``jobs_count``,
            ``todo``, ``doing``, ``succeeded``, ``failed``).
        """
        return [
            {
                "name": row["name"],
                "jobs_count": row["jobs_count"],
                "todo": row["stats"].get("todo", 0),
                "doing": row["stats"].get("doing", 0),
                "succeeded": row["stats"].get("succeeded", 0),
                "failed": row["stats"].get("failed", 0),
            }
            for row in await self.connector.execute_query_all_async(
                query=sql.queries["list_queues"],
                queue_name=queue,
                task_name=task,
                status=status,
                lock=lock,
            )
        ]

    async def list_tasks_async(
        self,
        queue: Optional[str] = None,
        task: Optional[str] = None,
        status: Optional[str] = None,
        lock: Optional[str] = None,
    ) -> Iterable[Dict[str, Any]]:
        """
        List all tasks and number of jobs per status for each task.

        Parameters
        ----------
        queue : ``str``
            Filter by job queue name
        task : ``str``
            Filter by job task name
        status : ``str``
            Filter by job status (*todo*/*doing*/*succeeded*/*failed*)
        lock : ``str``
            Filter by job lock

        Returns
        -------
        ``List[Dict[str, Any]]``
            A list of dictionaries representing tasks stats (``name``, ``jobs_count``,
            ``todo``, ``doing``, ``succeeded``, ``failed``).
        """
        return [
            {
                "name": row["name"],
                "jobs_count": row["jobs_count"],
                "todo": row["stats"].get("todo", 0),
                "doing": row["stats"].get("doing", 0),
                "succeeded": row["stats"].get("succeeded", 0),
                "failed": row["stats"].get("failed", 0),
            }
            for row in await self.connector.execute_query_all_async(
                query=sql.queries["list_tasks"],
                queue_name=queue,
                task_name=task,
                status=status,
                lock=lock,
            )
        ]

    async def set_job_status_async(self, id: int, status: str) -> Dict[str, Any]:
        """
        Set/reset the status of a specific job.

        Parameters
        ----------
        id : ``int``
            Job ID
        status : ``str``
            New job status (*todo*/*doing*/*succeeded*/*failed*)

        Returns
        -------
        ``Dict[str, Any]``
            A dictionary representing the job (``id``, ``queue``, ``task``,
            ``lock``, ``args``, ``status``, ``scheduled_at``, ``attempts``).
        """
        await self.connector.execute_query_async(
            query=sql.queries["set_job_status"], id=id, status=status,
        )
        (result,) = await self.list_jobs_async(id=id)
        return result
