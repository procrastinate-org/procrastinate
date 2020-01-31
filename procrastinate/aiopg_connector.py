import asyncio
from typing import Any, Callable, Dict, List, Optional

import aiopg
import psycopg2.sql
from psycopg2.extras import Json, RealDictCursor

from procrastinate import store


def wrap_json(arguments: Dict[str, Any], json_dumps: Optional[Callable]):
    return {
        key: Json(value, dumps=json_dumps) if isinstance(value, dict) else value
        for key, value in arguments.items()
    }


async def get_connection(
    dsn="", json_loads: Optional[Callable] = None, **kwargs
) -> aiopg.Connection:
    # tell aiopg not to register adapters for hstore & json by default, as
    # those are registered at the module level and could overwrite previously
    # defined adapters
    kwargs.setdefault("enable_json", False)
    kwargs.setdefault("enable_hstore", False)
    kwargs.setdefault("enable_uuid", False)
    conn = await aiopg.connect(dsn=dsn, **kwargs)
    if json_loads:
        psycopg2.extras.register_default_jsonb(conn.raw, loads=json_loads)
    return conn


def connection_is_open(connection: aiopg.Connection) -> bool:
    return not connection.closed


async def execute_query(
    connection: aiopg.Connection,
    query: str,
    json_dumps: Optional[Callable],
    **arguments: Any
) -> None:
    # aiopg can work with psycopg2's cursor class
    async with connection.cursor(cursor_factory=RealDictCursor) as cursor:
        await cursor.execute(query, wrap_json(arguments, json_dumps))


async def execute_query_one(
    connection: aiopg.Connection,
    query: str,
    json_dumps: Optional[Callable],
    **arguments: Any
) -> Dict[str, Any]:
    # aiopg can work with psycopg2's cursor class
    async with connection.cursor(cursor_factory=RealDictCursor) as cursor:
        await cursor.execute(query, wrap_json(arguments, json_dumps))

        return await cursor.fetchone()


async def execute_query_all(
    connection: aiopg.Connection,
    query: str,
    json_dumps: Optional[Callable],
    **arguments: Any
) -> List[Dict[str, Any]]:
    # aiopg can work with psycopg2's cursor class
    async with connection.cursor(cursor_factory=RealDictCursor) as cursor:
        await cursor.execute(query, wrap_json(arguments, json_dumps))

        return await cursor.fetchall()


def make_dynamic_query(query: str, **identifiers: str) -> str:
    return psycopg2.sql.SQL(query).format(
        **{key: psycopg2.sql.Identifier(value) for key, value in identifiers.items()}
    )


async def wait_for_jobs(connection: aiopg.Connection, socket_timeout: float):
    try:
        await asyncio.wait_for(connection.notifies.get(), timeout=socket_timeout)
    except asyncio.TimeoutError:
        pass


def interrupt_wait(connection: aiopg.Connection):
    asyncio.get_event_loop().call_soon_threadsafe(connection.notifies.put_nowait, "s")


class PostgresJobStore(store.BaseJobStore):
    """
    Uses ``aiopg`` to establish an asynchronous
    connection to a PostgreSQL database.
    """

    def __init__(
        self,
        *,
        socket_timeout: float = store.SOCKET_TIMEOUT,
        json_dumps: Optional[Callable] = None,
        json_loads: Optional[Callable] = None,
        **kwargs: Any
    ):
        """
        All parameters except ``socket_timeout``, ``json_dumps`` and ``json_loads``
        are passed to :py:func:`aiopg.connect` (see the documentation__)

        .. __: https://aiopg.readthedocs.io/en/stable/core.html#connection
        .. _psycopg2 doc: https://www.psycopg.org/docs/extras.html#json-adaptation

        Parameters
        ----------
        socket_timeout:
            This parameter should generally not be changed.
            It indicates the maximum duration (in seconds) procrastinate workers wait
            between each database job pull. Job activity will be pushed from the db to
            the worker, but in case the push mechanism fails somehow, workers will not
            stay idle longer than the number of seconds indicated by this parameters.
        json_dumps:
            The JSON dumps function to use for serializing job arguments. Defaults to
            the function used by psycopg2. See the `psycopg2 doc`_.
        json_loads:
            The JSON loads function to use for deserializing job arguments. Defaults
            to the function used by psycopg2. See the `psycopg2 doc`_.

        """

        self._connection_parameters = kwargs
        self._connection: Optional[aiopg.Connection] = None
        self.socket_timeout = socket_timeout
        self.json_dumps = json_dumps
        self.json_loads = json_loads

    async def get_connection(self):
        if not self._connection or not connection_is_open(self._connection):
            self._connection = await get_connection(
                json_loads=self.json_loads, **self._connection_parameters
            )
        return self._connection

    async def close_connection(self) -> None:
        if not self._connection:
            return

        await self._connection.close()

    async def execute_query(self, query: str, **arguments: Any) -> None:
        await execute_query(
            await self.get_connection(),
            query=query,
            json_dumps=self.json_dumps,
            **arguments
        )

    async def execute_query_one(self, query: str, **arguments: Any) -> Dict[str, Any]:
        return await execute_query_one(
            await self.get_connection(),
            query=query,
            json_dumps=self.json_dumps,
            **arguments
        )

    async def execute_query_all(
        self, query: str, **arguments: Any
    ) -> List[Dict[str, Any]]:
        return await execute_query_all(
            await self.get_connection(),
            query=query,
            json_dumps=self.json_dumps,
            **arguments
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
