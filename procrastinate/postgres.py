import os
import select
from typing import Any, Dict, List, Tuple

import psycopg2
from psycopg2 import extras
from psycopg2 import sql as psycopg2_sql
from psycopg2.extras import RealDictCursor

from procrastinate import store

SOCKET_TIMEOUT = 5.0  # seconds


def get_connection(*args, **kwargs) -> psycopg2._psycopg.connection:
    return psycopg2.connect(*args, **kwargs)


def init_pg_extensions() -> None:
    psycopg2.extensions.register_adapter(dict, extras.Json)


def execute_query(
    connection: psycopg2._psycopg.connection, query: str, **arguments: Any
) -> None:
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(query, arguments)
            connection.commit()


def execute_query_one(
    connection: psycopg2._psycopg.connection, query: str, **arguments: Any
) -> Dict[str, Any]:
    with connection:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, arguments)
            connection.commit()
            return cursor.fetchone()


def execute_query_all(
    connection: psycopg2._psycopg.connection, query: str, **arguments: Any
) -> List[Dict[str, Any]]:
    with connection:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, arguments)
            connection.commit()
            return cursor.fetchall()


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

    def execute_query(self, query: str, **arguments: Any) -> None:
        execute_query(self.connection, query=query, **arguments)

    def execute_query_one(self, query: str, **arguments: Any) -> Dict[str, Any]:
        return execute_query_one(self.connection, query=query, **arguments)

    def execute_query_all(self, query: str, **arguments: Any) -> List[Dict[str, Any]]:
        return execute_query_all(self.connection, query=query, **arguments)

    def wait_for_jobs(self) -> None:
        wait_for_jobs(
            connection=self.connection,
            socket_timeout=self.socket_timeout,
            stop_pipe=self.stop_pipe,
        )

    def stop(self):
        send_stop(stop_pipe=self.stop_pipe)

    def make_dynamic_query(self, query: str, **identifiers: str) -> str:
        return psycopg2_sql.SQL(query).format(
            **{
                key: psycopg2_sql.Identifier(value)
                for key, value in identifiers.items()
            }
        )
