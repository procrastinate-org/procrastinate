import os
import select
from typing import Any, Dict, List, Tuple, Optional

from psycopg2 import sql as psycopg2_sql
from psycopg2.extras import RealDictCursor

import aiopg

from procrastinate import store

SOCKET_TIMEOUT = 5.0  # seconds


async def get_connection(*args, **kwargs) -> aiopg.Connection:
    return await aiopg.connect(*args, **kwargs)


async def execute_query(
    connection: aiopg.Connection, query: str, **arguments: Any
) -> None:
    async with connection:
        async with connection.cursor() as cursor:
            await cursor.execute(query, arguments)


async def execute_query_one(
    connection: aiopg.Connection, query: str, **arguments: Any
) -> Dict[str, Any]:
    async with connection:
        async with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            await cursor.execute(query, arguments)

            return await cursor.fetchone()


async def execute_query_all(
    connection: aiopg.Connection, query: str, **arguments: Any
) -> List[Dict[str, Any]]:
    async with connection:
        async with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            await cursor.execute(query, arguments)
            return await cursor.fetchall()


def wait_for_jobs(
    connection: aiopg.Connection,
    socket_timeout: float,
    stop_pipe: Tuple[int, int],
) -> None:
    ready_fds = select.select([connection, stop_pipe[0]], [], [], socket_timeout)
    # Don't let things accumulate in the pipe
    if stop_pipe[0] in ready_fds[0]:
        os.read(stop_pipe[0], 1)


def send_stop(stop_pipe: Tuple[int, int]):
    os.write(stop_pipe[1], b"s")


class AiopgJobStore(store.AsyncBaseJobStore):
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

        self._connection_parameters = kwargs
        self._connection: Optional[aiopg.Connection] = None
        self.socket_timeout = socket_timeout
        self.stop_pipe = os.pipe()

    async def get_connection(self):
        if not self._connection:
            self._connection = await get_connection(**self._connection_parameters)
        return self._connection

    async def execute_query(self, query: str, **arguments: Any) -> None:
        await execute_query(await self.get_connection(), query=query, **arguments)

    async def execute_query_one(self, query: str, **arguments: Any) -> Dict[str, Any]:
        return await execute_query_one(await self.get_connection(), query=query, **arguments)

    async def execute_query_all(self, query: str, **arguments: Any) -> List[Dict[str, Any]]:
        return await execute_query_all(await self.get_connection(), query=query, **arguments)

    async def wait_for_jobs(self) -> None:
        wait_for_jobs(
            connection=await self.get_connection(),
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
