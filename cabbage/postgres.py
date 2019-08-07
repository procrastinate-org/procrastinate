import select
from typing import Iterable, Iterator, Optional

import psycopg2
from psycopg2 import extras, sql
from psycopg2.extras import RealDictCursor

from cabbage import jobs, store, types

insert_jobs_sql = """
INSERT INTO cabbage_jobs (queue_name, task_name, lock, args, scheduled_at)
VALUES (%(queue)s, %(task_name)s, %(lock)s, %(args)s, %(scheduled_at)s)
RETURNING id;
"""

select_jobs_sql = """
SELECT id, task_name, lock, args, scheduled_at, queue_name
    FROM cabbage_fetch_job(%(queues)s);
"""

select_stalled_jobs_sql = """
SELECT job.id, task_name, lock, args, scheduled_at, queue_name
    FROM cabbage_jobs job
WHERE status = 'doing'
  AND started_at < NOW() - (%(nb_seconds)s || 'SECOND')::INTERVAL
  AND (%(queue)s IS NULL OR queue_name = %(queue)s)
  AND (%(task_name)s IS NULL OR task_name = %(task_name)s)
"""

finish_job_sql = """
SELECT cabbage_finish_job(%(job_id)s, %(status)s);
"""

listen_queue_raw_sql = """
LISTEN {queue_name};
"""

listen_any_queue = "cabbage_any_queue"
listen_queue_pattern = "cabbage_queue#{queue}"


def get_connection(**kwargs) -> psycopg2._psycopg.connection:
    kwargs.setdefault("dsn", "")
    return psycopg2.connect(**kwargs)


def init_pg_extensions() -> None:
    psycopg2.extensions.register_adapter(dict, extras.Json)


def launch_job(connection: psycopg2._psycopg.connection, job: jobs.Job) -> int:
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(
                insert_jobs_sql,
                {
                    "task_name": job.task_name,
                    "lock": job.lock,
                    "args": job.task_kwargs,
                    "scheduled_at": job.scheduled_at,
                    "queue": job.queue,
                },
            )
            row = cursor.fetchone()

    return row[0]


def get_jobs(
    connection: psycopg2._psycopg.connection, queues: Optional[Iterable[str]]
) -> Iterator[types.JSONDict]:
    with connection.cursor(cursor_factory=RealDictCursor) as cursor:
        while True:
            cursor.execute(select_jobs_sql, {"queues": queues})
            connection.commit()

            row = cursor.fetchone()

            # fetch_tasks will always return a row, but is there's no relevant
            # value, it will all be None
            if row["id"] is None:
                return

            yield {
                "id": row["id"],
                "lock": row["lock"],
                "task_name": row["task_name"],
                "task_kwargs": row["args"],
                "scheduled_at": row["scheduled_at"],
                "queue": row["queue_name"],
            }


def get_stalled_jobs(
    connection: psycopg2._psycopg.connection,
    nb_seconds: int,
    queue: str = None,
    task_name: str = None,
) -> Iterator[types.JSONDict]:
    with connection:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                select_stalled_jobs_sql,
                {"nb_seconds": nb_seconds, "queue": queue, "task_name": task_name},
            )

            rows = cursor.fetchall()
            for row in rows:
                yield {
                    "id": row["id"],
                    "lock": row["lock"],
                    "task_name": row["task_name"],
                    "task_kwargs": row["args"],
                    "scheduled_at": row["scheduled_at"],
                    "queue": row["queue_name"],
                }


def finish_job(
    connection: psycopg2._psycopg.connection, job_id: int, status: str
) -> None:
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(finish_job_sql, {"job_id": job_id, "status": status})


def listen_queues(
    connection: psycopg2._psycopg.connection, queues: Optional[Iterable[str]] = None
) -> None:
    if queues is None:
        listen_to = [listen_any_queue]
    else:
        listen_to = [listen_queue_pattern.format(queue=queue) for queue in queues]

    queries = [
        sql.SQL(listen_queue_raw_sql).format(queue_name=sql.Identifier(element))
        for element in listen_to
    ]

    with connection:
        with connection.cursor() as cursor:
            for query in queries:
                cursor.execute(query)


def wait_for_jobs(connection: psycopg2._psycopg.connection, timeout: float) -> None:
    select.select([connection], [], [], timeout)


init_pg_extensions()


class PostgresJobStore(store.JobStore):
    def __init__(self, **kwargs):
        self.connection = get_connection(**kwargs)

    def launch_job(self, job: jobs.Job) -> int:
        return launch_job(connection=self.connection, job=job)

    def get_jobs(self, queues: Optional[Iterable[str]]) -> Iterator[jobs.Job]:
        for job_dict in get_jobs(connection=self.connection, queues=queues):
            # Hard to tell mypy that every element of the dict is typed correctly
            yield jobs.Job(job_store=self, **job_dict)  # type: ignore

    def get_stalled_jobs(
        self,
        nb_seconds: int,
        queue: Optional[str] = None,
        task_name: Optional[str] = None,
    ) -> Iterator[jobs.Job]:
        job_dicts = get_stalled_jobs(
            self.connection, nb_seconds=nb_seconds, queue=queue, task_name=task_name
        )
        for job_dict in job_dicts:
            yield jobs.Job(job_store=self, **job_dict)  # type: ignore

    def finish_job(self, job: jobs.Job, status: jobs.Status) -> None:
        assert job.id
        return finish_job(
            connection=self.connection, job_id=job.id, status=status.value
        )

    def listen_for_jobs(self, queues: Optional[Iterable[str]] = None) -> None:
        listen_queues(connection=self.connection, queues=queues)

    def wait_for_jobs(self, timeout: float) -> None:
        wait_for_jobs(connection=self.connection, timeout=timeout)
