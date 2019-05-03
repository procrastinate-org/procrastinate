import select
from typing import Iterator, Optional

import psycopg2
from psycopg2 import extras, sql
from psycopg2.extras import RealDictCursor

from cabbage import exceptions, jobs, store, types

insert_jobs_sql = """
INSERT INTO cabbage_jobs (queue_id, task_name, lock, args)
SELECT id, %(task_name)s, %(lock)s, %(args)s
    FROM cabbage_queues WHERE queue_name=%(queue)s
RETURNING id;
"""

select_jobs_sql = """
SELECT id, task_name, lock, args FROM cabbage_fetch_job(%(queue)s);
"""
finish_job_sql = """
SELECT cabbage_finish_job(%(job_id)s, %(status)s);
"""
insert_queue_sql = """
INSERT INTO cabbage_queues (queue_name)
VALUES (%(queue)s)
ON CONFLICT DO NOTHING
RETURNING id
"""

listen_queue_raw_sql = """
LISTEN {queue_name};
"""


def get_connection(**kwargs) -> psycopg2._psycopg.connection:
    return psycopg2.connect("", **kwargs)


def init_pg_extensions() -> None:
    psycopg2.extensions.register_adapter(dict, extras.Json)


def launch_job(connection: psycopg2._psycopg.connection, job: jobs.Job) -> int:
    with connection.cursor() as cursor:
        cursor.execute(
            insert_jobs_sql,
            {
                "task_name": job.task_name,
                "lock": job.lock,
                "args": job.task_kwargs,
                "queue": job.queue,
            },
        )
        row = cursor.fetchone()

    if not row:
        raise exceptions.QueueNotFound(job.queue)

    connection.commit()
    return row[0]


def get_jobs(
    connection: psycopg2._psycopg.connection, queue: str
) -> Iterator[types.JSONDict]:
    with connection.cursor(cursor_factory=RealDictCursor) as cursor:
        while True:
            cursor.execute(select_jobs_sql, {"queue": queue})
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
                "queue": queue,
            }


def finish_job(
    connection: psycopg2._psycopg.connection, job_id: int, status: str
) -> None:
    with connection.cursor() as cursor:
        cursor.execute(finish_job_sql, {"job_id": job_id, "status": status})

    connection.commit()


def register_queue(
    connection: psycopg2._psycopg.connection, queue: str
) -> Optional[int]:
    with connection.cursor() as cursor:
        cursor.execute(insert_queue_sql, {"queue": queue})
        row = cursor.fetchone()

    connection.commit()

    return row[0] if row else None


def listen_queue(connection: psycopg2._psycopg.connection, queue: str) -> None:
    queue_name = sql.Identifier(f"cabbage_queue#{queue}")
    query = sql.SQL(listen_queue_raw_sql).format(queue_name=queue_name)

    with connection.cursor() as cursor:
        cursor.execute(query)


def wait_for_jobs(connection: psycopg2._psycopg.connection, timeout: int) -> None:
    select.select([connection], [], [], timeout)


init_pg_extensions()


class PostgresJobStore(store.JobStore):
    def __init__(self, connection: Optional[psycopg2._psycopg.connection] = None):
        self.connection = connection or get_connection()

    def register_queue(self, queue: str) -> Optional[int]:
        return register_queue(connection=self.connection, queue=queue)

    def launch_job(self, job: jobs.Job) -> int:
        return launch_job(connection=self.connection, job=job)

    def get_jobs(self, queue: str) -> Iterator[jobs.Job]:
        for job_dict in get_jobs(connection=self.connection, queue=queue):
            # Hard to tell mypy that every element of the dict is typed correctly
            yield jobs.Job(job_store=self, **job_dict)  # type: ignore

    def finish_job(self, job: jobs.Job, status: jobs.Status) -> None:
        assert job.id
        return finish_job(
            connection=self.connection, job_id=job.id, status=status.value
        )

    def listen_for_jobs(self, queue: str) -> None:
        listen_queue(connection=self.connection, queue=queue)

    def wait_for_jobs(self, timeout: int) -> None:
        wait_for_jobs(connection=self.connection, timeout=timeout)
