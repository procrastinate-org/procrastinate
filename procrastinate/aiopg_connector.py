import asyncio
from typing import Any, Dict, List, Optional

from psycopg2.extras import RealDictCursor, Json

import aiopg
from procrastinate import psycopg2_connector, store


async def get_connection(*args, **kwargs) -> aiopg.Connection:
    return await aiopg.connect(*args, **kwargs)


def wrap_json(arguments: Dict[str, Any]):
    return {
        key: Json(value) if isinstance(value, dict) else value
        for key, value in arguments.items()
    }


async def execute_query(
    connection: aiopg.Connection, query: str, **arguments: Any
) -> None:
    async with connection.cursor() as cursor:
        await cursor.execute(query, wrap_json(arguments))


async def execute_query_one(
    connection: aiopg.Connection, query: str, **arguments: Any
) -> Dict[str, Any]:
    # Strangely, aiopg can work with psycopg2's cursor class.
    async with connection.cursor(cursor_factory=RealDictCursor) as cursor:
        await cursor.execute(query, wrap_json(arguments))

        return await cursor.fetchone()


async def execute_query_all(
    connection: aiopg.Connection, query: str, **arguments: Any
) -> List[Dict[str, Any]]:
    async with connection.cursor(cursor_factory=RealDictCursor) as cursor:
        await cursor.execute(query, wrap_json(arguments))
        return await cursor.fetchall()


class AiopgJobStore(store.AsyncBaseJobStore):
    """
    Uses `psycopg2` to establish a synchronous
    connection to a Postgres database.
    """

    def __init__(self, *, socket_timeout: float = store.SOCKET_TIMEOUT, **kwargs: Any):
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

    async def get_connection(self):
        if not self._connection:
            self._connection = await get_connection(**self._connection_parameters)
        return self._connection

    async def execute_query(self, query: str, **arguments: Any) -> None:
        await execute_query(await self.get_connection(), query=query, **arguments)

    async def execute_query_one(self, query: str, **arguments: Any) -> Dict[str, Any]:
        return await execute_query_one(
            await self.get_connection(), query=query, **arguments
        )

    async def execute_query_all(
        self, query: str, **arguments: Any
    ) -> List[Dict[str, Any]]:
        return await execute_query_all(
            await self.get_connection(), query=query, **arguments
        )

    def make_dynamic_query(self, query: str, **identifiers: str) -> str:
        return psycopg2_connector.make_dynamic_query(query=query, **identifiers)

    async def wait_for_jobs(self):
        connection = await self.get_connection()
        await asyncio.wait_for(connection.notifies.get(), timeout=self.socket_timeout)

    def stop(self):
        if self._connection:
            self._connection.notifies.put_nowait("s")
