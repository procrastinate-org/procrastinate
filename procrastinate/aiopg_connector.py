from typing import Any, Awaitable, Dict, Optional

import aiopg
from psycopg2.extras import RealDictCursor

from procrastinate import psycopg2_connector, store


def get_connection(**kwargs) -> Awaitable[aiopg.Connection]:
    return aiopg.connect(**kwargs)


async def execute_query_one(
    connection: aiopg.Connection, query: str, **arguments: Any
) -> Dict[str, Any]:
    # Strangely, aiopg can work with psycopg2's cursor class.
    async with connection.cursor(cursor_factory=RealDictCursor) as cursor:
        await cursor.execute(query, psycopg2_connector.wrap_json(arguments))

        return await cursor.fetchone()


class AiopgJobStore(store.AsyncBaseJobStore):
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

    async def execute_query_one(self, query: str, **arguments: Any) -> Dict[str, Any]:
        return await execute_query_one(
            await self.get_connection(), query=query, **arguments
        )

    def get_sync_store(self) -> store.BaseJobStore:
        from procrastinate.psycopg2_connector import PostgresJobStore

        return PostgresJobStore(
            socket_timeout=self.socket_timeout, **self._connection_parameters
        )
