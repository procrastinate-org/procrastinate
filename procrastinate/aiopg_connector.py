import asyncio
from typing import Any, Awaitable, Dict, List, Optional

import aiopg
import psycopg2.sql
from psycopg2.extras import Json, RealDictCursor

from procrastinate import store


def wrap_json(arguments: Dict[str, Any]):
    return {
        key: Json(value) if isinstance(value, dict) else value
        for key, value in arguments.items()
    }


def get_connection(dsn="", **kwargs) -> Awaitable[aiopg.Connection]:
    return aiopg.connect(dsn=dsn, **kwargs)


async def execute_query(
    connection: aiopg.Connection, query: str, **arguments: Any
) -> None:
    # Strangely, aiopg can work with psycopg2's cursor class.
    async with connection.cursor(cursor_factory=RealDictCursor) as cursor:
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
    # Strangely, aiopg can work with psycopg2's cursor class.
    async with connection.cursor(cursor_factory=RealDictCursor) as cursor:
        await cursor.execute(query, wrap_json(arguments))

        return await cursor.fetchall()


def make_dynamic_query(query: str, **identifiers: str) -> str:
    return psycopg2.sql.SQL(query).format(
        **{key: psycopg2.sql.Identifier(value) for key, value in identifiers.items()}
    )


async def wait_for_jobs(connection: aiopg.Connection, socket_timeout: float):
    try:
        await asyncio.wait_for(connection.notifies.get(), timeout=socket_timeout)
    except asyncio.futures.TimeoutError:
        pass


def interrupt_wait(connection: aiopg.Connection):
    asyncio.get_event_loop().call_soon_threadsafe(connection.notifies.put_nowait, "s")


class PostgresJobStore(store.BaseJobStore):
    """
    Uses ``aiopg`` to establish an asynchronous
    connection to a Postgres database.
    """

    def __init__(self, *, socket_timeout: float = store.SOCKET_TIMEOUT, **kwargs: Any):
        """
        All parameters except ``socket_timeout`` are passed to
        :py:func:`aiopg.connect` (see the documentation__)

        .. __: https://aiopg.readthedocs.io/en/stable/core.html#connection

        Parameters
        ----------
        socket_timeout:
            This parameter should generally not be changed.
            It indicates the maximum duration (in seconds) procrastinate workers wait
            between each database job pull. Job activity will be pushed from the db to
            the worker, but in case the push mechanism fails somehow, workers will not
            stay idle longer than the number of seconds indicated by this parameters.
        """

        self._connection_parameters = kwargs
        self._connection: Optional[aiopg.Connection] = None
        self.socket_timeout = socket_timeout

    async def get_connection(self):
        if not self._connection:
            self._connection = await get_connection(**self._connection_parameters)
        return self._connection

    async def close_connection(self) -> None:
        if not self._connection:
            return

        await self._connection.close()

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
        return make_dynamic_query(query=query, **identifiers)

    async def wait_for_jobs(self):
        return await wait_for_jobs(
            connection=await self.get_connection(), socket_timeout=self.socket_timeout
        )

    def stop(self):
        if self._connection:
            interrupt_wait(connection=self._connection)
