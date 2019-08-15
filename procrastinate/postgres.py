import datetime
import os
import select
from typing import Any, Iterable, Iterator, Optional, Tuple

import psycopg2
from psycopg2 import extras, sql
from psycopg2.extras import RealDictCursor

from procrastinate import jobs, store, types

SOCKET_TIMEOUT = 5.0  # seconds

insert_jobs_sql = """
INSERT INTO procrastinate_jobs (queue_name, task_name, lock, args, scheduled_at)
VALUES (%(queue)s, %(task_name)s, %(lock)s, %(args)s, %(scheduled_at)s)
RETURNING id;
"""

select_jobs_sql = """
SELECT id, task_name, lock, args, scheduled_at, queue_name
    FROM procrastinate_fetch_job(%(queues)s);
"""

select_stalled_jobs_sql = """
SELECT job.id, task_name, lock, args, scheduled_at, queue_name
    FROM procrastinate_jobs job
WHERE status = 'doing'
  AND started_at < NOW() - (%(nb_seconds)s || 'SECOND')::INTERVAL
  AND (%(queue)s IS NULL OR queue_name = %(queue)s)
  AND (%(task_name)s IS NULL OR task_name = %(task_name)s)
"""

finish_job_sql = """
SELECT procrastinate_finish_job(%(job_id)s, %(status)s, %(scheduled_at)s);
"""

listen_queue_raw_sql = """
LISTEN {queue_name};
"""

listen_any_queue = "procrastinate_any_queue"
listen_queue_pattern = "procrastinate_queue#{queue}"


def get_connection(*args, **kwargs) -> psycopg2._psycopg.connection:
    return psycopg2.connect(*args, **kwargs)


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
    connection: psycopg2._psycopg.connection,
    job_id: int,
    status: str,
    scheduled_at: Optional[datetime.datetime] = None,
) -> None:
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(
                finish_job_sql,
                {"job_id": job_id, "status": status, "scheduled_at": scheduled_at},
            )


def listen_queues(
    connection: psycopg2._psycopg.connection, queues: Optional[Iterable[str]]
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


def wait_for_jobs(
    connection: psycopg2._psycopg.connection,
    socket_timeout: float,
    stop_pipe: Tuple[int, int],
) -> None:
    ready_fds = select.select([connection, stop_pipe[0]], [], [], socket_timeout)
    # Don't let things accumulate in the pipe
    if stop_pipe[0] in ready_fds[0]:
        os.read(stop_pipe[0], 1)


def send_stop(stop_pipe: Tuple[int, int]):
    os.write(stop_pipe[1], b"s")


init_pg_extensions()


class PostgresJobStore(store.BaseJobStore):
    """
    Uses `psycopg2` to establish a synchronous
    connection to a Postgres database.
    """

    def __init__(self, *, socket_timeout: float = SOCKET_TIMEOUT, **kwargs: Any):
        """
        All parameters except `socket_timeout` are passed to
        :py:func:`psycopg2.connect` (see the documentation_)

        .. _documentation: http://initd.org/psycopg/docs/module.html#psycopg2.connect

        Parameters
        ----------
        socket_timeout:
            This parameter should generally not be changed.
            It indicates how long procrastinate waits (in seconds) between
            renewing the socket `select` calls when waiting for tasks.
            The shorter the timeout, the more `select` calls it does.
            The longer the timeout, the longer the server will wait idle if, for
            some reason, the postgres LISTEN call doesn't work.
        """
        self.connection = get_connection(**kwargs)
        self.socket_timeout = socket_timeout
        self.stop_pipe = os.pipe()

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

    def finish_job(
        self,
        job: jobs.Job,
        status: jobs.Status,
        scheduled_at: Optional[datetime.datetime] = None,
    ) -> None:
        assert job.id
        return finish_job(
            connection=self.connection,
            job_id=job.id,
            status=status.value,
            scheduled_at=scheduled_at,
        )

    def listen_for_jobs(self, queues: Optional[Iterable[str]] = None) -> None:
        listen_queues(connection=self.connection, queues=queues)

    def wait_for_jobs(self) -> None:
        wait_for_jobs(
            connection=self.connection,
            socket_timeout=self.socket_timeout,
            stop_pipe=self.stop_pipe,
        )

    def stop(self):
        send_stop(stop_pipe=self.stop_pipe)
