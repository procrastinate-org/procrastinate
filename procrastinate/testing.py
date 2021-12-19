import asyncio
import datetime
from collections import Counter
from itertools import count
from typing import Any, Dict, Iterable, List, Optional, Tuple

from procrastinate import connector, exceptions, schema, sql, types, utils

JobRow = Dict[str, Any]
EventRow = Dict[str, Any]


class InMemoryConnector(connector.BaseAsyncConnector):
    """
    An InMemoryConnector may be used for testing only. Tasks are not
    persisted and will be lost when the process ends.

    While implementing the Connector interface, it also adds a few
    methods and attributes to ease testing.
    """

    def __init__(self):
        """
        Attributes
        ----------
        jobs : ``Dict[int, Dict]``
            Mapping of ``{<job id>: <Job database row as a dictionary>}``
        """
        self.reset()
        self.reverse_queries = {value: key for key, value in sql.queries.items()}
        self.reverse_queries[schema.SchemaManager.get_schema()] = "apply_schema"

    def reset(self):
        """
        Removes anything the in-memory pseudo-database contains, to ensure test
        independence.
        """
        self.jobs: Dict[int, JobRow] = {}
        self.events: Dict[int, List[EventRow]] = {}
        self.job_counter = count(1)
        self.queries: List[Tuple[str, Dict[str, Any]]] = []
        self.notify_event = None
        self.notify_channels = []
        self.periodic_defers: Dict[Tuple[str, str], int] = {}
        self.table_exists = True
        self.states: List[str] = []

    def generic_execute(self, query, suffix, **arguments) -> Any:
        """
        Calling a query will call the <query_name>_<suffix> method
        on this class. Suffix is "run" if no result is expected,
        "one" if a single result, and "all" if multiple results.
        """
        query_name = self.reverse_queries[query]
        self.queries.append((query_name, arguments))
        return getattr(self, f"{query_name}_{suffix}")(**arguments)

    def make_dynamic_query(self, query, **identifiers: str) -> str:
        return query.format(**identifiers)

    async def execute_query_async(self, query: str, **arguments: Any) -> None:
        self.generic_execute(query, "run", **arguments)

    async def execute_query_one_async(
        self, query: str, **arguments: Any
    ) -> Dict[str, Any]:
        return self.generic_execute(query, "one", **arguments)

    async def execute_query_all_async(
        self, query: str, **arguments: Any
    ) -> List[Dict[str, Any]]:
        return self.generic_execute(query, "all", **arguments)

    async def listen_notify(
        self, event: asyncio.Event, channels: Iterable[str]
    ) -> None:
        self.notify_event = event
        self.notify_channels = channels

    def open(self, pool: Optional[connector.Pool] = None) -> None:
        self.states.append("open")

    async def open_async(self, pool: Optional[connector.Pool] = None) -> None:
        self.states.append("open_async")

    def close(self) -> None:
        self.states.append("closed")

    async def close_async(self) -> None:
        self.states.append("closed_async")

    # End of BaseConnector methods

    def defer_job_one(
        self,
        task_name: str,
        lock: Optional[str],
        queueing_lock: Optional[str],
        args: types.JSONDict,
        scheduled_at: Optional[datetime.datetime],
        queue: str,
    ) -> JobRow:
        if queueing_lock is not None and any(
            job["queueing_lock"] == queueing_lock and job["status"] == "todo"
            for job in self.jobs.values()
        ):
            from . import manager

            raise exceptions.UniqueViolation(
                constraint_name=manager.QUEUEING_LOCK_CONSTRAINT
            )

        id = next(self.job_counter)

        self.jobs[id] = job_row = {
            "id": id,
            "queue_name": queue,
            "task_name": task_name,
            "lock": lock,
            "queueing_lock": queueing_lock,
            "args": args,
            "status": "todo",
            "scheduled_at": scheduled_at,
            "attempts": 0,
        }
        self.events[id] = []
        if scheduled_at:
            self.events[id].append({"type": "scheduled", "at": scheduled_at})
        self.events[id].append({"type": "deferred", "at": utils.utcnow()})
        if self.notify_event:
            if "procrastinate_any_queue" in self.notify_channels or (
                f"procrastinate_queue#{queue}" in self.notify_channels
            ):
                self.notify_event.set()
        return job_row

    def defer_periodic_job_one(
        self,
        queue: str,
        task_name: str,
        args: types.JSONDict,
        defer_timestamp: int,
        lock: Optional[str],
        queueing_lock: Optional[str],
        periodic_id: str,
    ):
        # If the periodic task has already been deferred for this timestamp
        if self.periodic_defers.get((task_name, periodic_id)) == defer_timestamp:
            return {"id": None}

        self.periodic_defers[(task_name, periodic_id)] = defer_timestamp
        return self.defer_job_one(
            task_name=task_name,
            queue=queue,
            lock=lock,
            queueing_lock=queueing_lock,
            args=args,
            scheduled_at=None,
        )

    @property
    def current_locks(self) -> Iterable[str]:
        return {
            job["lock"] for job in self.jobs.values() if job["status"] == "doing"
        } - {None}

    @property
    def finished_jobs(self) -> List[JobRow]:
        return [
            job
            for job in self.jobs.values()
            if job["status"] in {"failed", "succeeded"}
        ]

    def fetch_job_one(self, queues: Optional[Iterable[str]]) -> Dict:
        # Creating a copy of the iterable so that we can modify it while we iterate

        for job in self.jobs.values():
            if (
                job["status"] == "todo"
                and (queues is None or job["queue_name"] in queues)
                and (not job["scheduled_at"] or job["scheduled_at"] <= utils.utcnow())
                and job["lock"] not in self.current_locks
            ):
                job["status"] = "doing"
                self.events[job["id"]].append({"type": "started", "at": utils.utcnow()})

                return job

        return {"id": None}

    def finish_job_run(self, job_id: int, status: str, delete_job: bool) -> None:
        if delete_job:
            self.jobs.pop(job_id)
            return

        job_row = self.jobs[job_id]
        job_row["status"] = status
        job_row["attempts"] += 1
        self.events[job_id].append({"type": status, "at": utils.utcnow()})

    def retry_job_run(self, job_id: int, retry_at: datetime.datetime) -> None:
        job_row = self.jobs[job_id]
        job_row["status"] = "todo"
        job_row["attempts"] += 1
        job_row["scheduled_at"] = retry_at
        self.events[job_id].append({"type": "scheduled", "at": retry_at})
        self.events[job_id].append({"type": "deferred_for_retry", "at": utils.utcnow()})

    def select_stalled_jobs_all(self, nb_seconds, queue, task_name):
        return (
            job
            for job in self.jobs.values()
            if job["status"] == "doing"
            and self.events[job["id"]][-1]["at"]
            < utils.utcnow() - datetime.timedelta(seconds=nb_seconds)
            and queue in (job["queue_name"], None)
            and task_name in (job["task_name"], None)
        )

    def delete_old_jobs_run(self, nb_hours, queue, statuses):
        for id, job in list(self.jobs.items()):

            if (
                job["status"] in statuses
                and (
                    max(e["at"] for e in self.events[id])
                    < utils.utcnow() - datetime.timedelta(hours=nb_hours)
                )
                and queue in (job["queue_name"], None)
            ):
                self.jobs.pop(id)

    def listen_for_jobs_run(self) -> None:
        pass

    def apply_schema_run(self) -> None:
        pass

    def list_jobs_all(self, **kwargs):
        for job in self.jobs.values():
            if all(
                expected is None or str(job[key]) == str(expected)
                for key, expected in kwargs.items()
            ):
                yield job

    def list_queues_all(self, **kwargs):
        jobs = list(self.list_jobs_all(**kwargs))
        queues = sorted({job["queue_name"] for job in jobs})
        for queue in queues:
            queue_jobs = [job for job in jobs if job["queue_name"] == queue]
            stats = Counter(job["status"] for job in queue_jobs)
            yield {"name": queue, "jobs_count": len(queue_jobs), "stats": stats}

    def list_tasks_all(self, **kwargs):
        jobs = list(self.list_jobs_all(**kwargs))
        tasks = sorted({job["task_name"] for job in jobs})
        for task in tasks:
            task_jobs = [job for job in jobs if job["task_name"] == task]
            stats = Counter(job["status"] for job in task_jobs)
            yield {"name": task, "jobs_count": len(task_jobs), "stats": stats}

    def list_locks_all(self, **kwargs):
        jobs = list(self.list_jobs_all(**kwargs))
        locks = sorted({job["lock"] for job in jobs})
        for lock in locks:
            lock_jobs = [job for job in jobs if job["lock"] == lock]
            stats = Counter(job["status"] for job in lock_jobs)
            yield {"name": lock, "jobs_count": len(lock_jobs), "stats": stats}

    def set_job_status_run(self, id, status):
        id = int(id)
        self.jobs[id]["status"] = status

    def check_connection_one(self):
        return {"check": self.table_exists or None}
