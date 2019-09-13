import datetime
import os
import select
from typing import Any, Iterable, Iterator, Optional, Tuple

import psycopg2
from psycopg2 import extras
from psycopg2 import sql as psycopg2_sql
from psycopg2.extras import RealDictCursor

from procrastinate import jobs, sql, store, types

SOCKET_TIMEOUT = 5.0  # seconds


def get_connection(*args, **kwargs) -> psycopg2._psycopg.connection:
    return psycopg2.connect(*args, **kwargs)


def init_pg_extensions() -> None:
    psycopg2.extensions.register_adapter(dict, extras.Json)


def defer_job(connection: psycopg2._psycopg.connection, job: jobs.Job) -> int:
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(
                sql.queries["insert_job"],
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


def get_job(
    connection: psycopg2._psycopg.connection, queues: Optional[Iterable[str]]
) -> Optional[types.JSONDict]:
    with connection.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(sql.queries["fetch_job"], {"queues": queues})
        connection.commit()

        row = cursor.fetchone()

        # fetch_tasks will always return a row, but is there's no relevant
        # value, it will all be None
        if row["id"] is None:
            return None

        return {
            "id": row["id"],
            "lock": row["lock"],
            "task_name": row["task_name"],
            "task_kwargs": row["args"],
            "scheduled_at": row["scheduled_at"],
            "queue": row["queue_name"],
            "attempts": row["attempts"],
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
                sql.queries["select_stalled_jobs"],
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
                    "attempts": row["attempts"],
                }


def delete_old_jobs(
    connection: psycopg2._psycopg.connection,
    nb_hours: int,
    statuses: Iterable[str],
    queue: str = None,
) -> None:
    with connection:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                sql.queries["delete_old_jobs"],
                {"nb_hours": nb_hours, "queue": queue, "statuses": tuple(statuses)},
            )


def finish_job(
    connection: psycopg2._psycopg.connection,
    job_id: int,
    status: str,
    scheduled_at: Optional[datetime.datetime] = None,
) -> None:
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(
                sql.queries["finish_job"],
                {"job_id": job_id, "status": status, "scheduled_at": scheduled_at},
            )


def channel_names(queues: Optional[Iterable[str]]) -> Iterable[str]:
    if queues is None:
        return ["procrastinate_any_queue"]
    else:
        return ["procrastinate_queue#" + queue for queue in queues]


def listen_queues(
    connection: psycopg2._psycopg.connection, queues: Optional[Iterable[str]]
) -> None:

    with connection:
        with connection.cursor() as cursor:
            for channel_name in channel_names(queues=queues):
                query = psycopg2_sql.SQL(sql.queries["listen_queue"]).format(
                    channel_name=psycopg2_sql.Identifier(channel_name)
                )
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

    def get_connection(self):
        return self.connection

    def defer_job(self, job: jobs.Job) -> int:
        return defer_job(connection=self.connection, job=job)

    def get_job(self, queues: Optional[Iterable[str]]) -> Optional[jobs.Job]:
        job_dict = get_job(connection=self.connection, queues=queues)
        if not job_dict:
            return None
        # Hard to tell mypy that every element of the dict is typed correctly
        return jobs.Job(  # type: ignore
            **job_dict
        )

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
            yield jobs.Job(**job_dict)  # type: ignore

    def delete_old_jobs(
        self,
        nb_hours: int,
        queue: Optional[str] = None,
        include_error: Optional[bool] = False,
    ) -> None:
        # We only consider finished jobs by default
        if not include_error:
            statuses = [jobs.Status.SUCCEEDED.value]
        else:
            statuses = [jobs.Status.SUCCEEDED.value, jobs.Status.FAILED.value]

        delete_old_jobs(
            self.connection, nb_hours=nb_hours, queue=queue, statuses=statuses
        )

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
