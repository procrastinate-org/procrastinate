import asyncio
import logging
import warnings
from typing import Any, Callable, Dict, List, Optional

import aiopg
import psycopg2.sql
from psycopg2.extras import Json, RealDictCursor

from procrastinate import connector

logger = logging.getLogger(__name__)


class PostgresConnector(connector.BaseConnector):
    def __init__(
        self,
        dsn="",
        socket_timeout: float = connector.SOCKET_TIMEOUT,
        json_dumps: Optional[Callable] = None,
        json_loads: Optional[Callable] = None,
        **kwargs: Any,
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
        kwargs["dsn"] = dsn
        self._connection_parameters = kwargs
        self._connection: Optional[aiopg.Connection] = None
        self._lock = asyncio.Lock()
        self.socket_timeout = socket_timeout
        self.json_dumps = json_dumps
        self.json_loads = json_loads

    async def close_connection(self) -> None:
        if not self._connection or self._connection.closed:
            return
        await self._connection.close()

    def _wrap_json(self, arguments: Dict[str, Any]):
        return {
            key: Json(value, dumps=self.json_dumps)
            if isinstance(value, dict)
            else value
            for key, value in arguments.items()
        }

    async def _get_connection(self) -> aiopg.Connection:
        # fast path
        if self._connection and not self._connection.closed:
            return self._connection
        async with self._lock:
            if self._connection and not self._connection.closed:
                return self._connection
            # tell aiopg not to register adapters for hstore & json by default, as
            # those are registered at the module level and could overwrite previously
            # defined adapters
            kwargs = self._connection_parameters
            kwargs.setdefault("enable_json", False)
            kwargs.setdefault("enable_hstore", False)
            kwargs.setdefault("enable_uuid", False)
            conn = await aiopg.connect(**kwargs)
            if self.json_loads:
                psycopg2.extras.register_default_jsonb(conn.raw, loads=self.json_loads)
            self._connection = conn
            return conn

    async def execute_query(self, query: str, **arguments: Any) -> None:
        connection = await self._get_connection()
        async with self._lock:
            # aiopg can work with psycopg2's cursor class
            async with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                await cursor.execute(query, self._wrap_json(arguments))

    async def execute_query_one(self, query: str, **arguments: Any) -> Dict[str, Any]:
        connection = await self._get_connection()
        async with self._lock:
            # aiopg can work with psycopg2's cursor class
            async with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                await cursor.execute(query, self._wrap_json(arguments))

                return await cursor.fetchone()

    async def execute_query_all(
        self, query: str, **arguments: Any
    ) -> List[Dict[str, Any]]:
        connection = await self._get_connection()
        async with self._lock:
            # aiopg can work with psycopg2's cursor class
            async with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                await cursor.execute(query, self._wrap_json(arguments))

                return await cursor.fetchall()

    def make_dynamic_query(self, query: str, **identifiers: str) -> str:
        return psycopg2.sql.SQL(query).format(
            **{
                key: psycopg2.sql.Identifier(value)
                for key, value in identifiers.items()
            }
        )

    async def wait_for_activity(self):
        connection = await self._get_connection()
        try:
            await asyncio.wait_for(
                connection.notifies.get(), timeout=self.socket_timeout
            )
        except asyncio.TimeoutError:
            pass

    # This can be called from a signal handler, better not do async stuff
    def interrupt_wait(self):
        if not self._connection or self._connection.closed:
            return
        asyncio.get_event_loop().call_soon_threadsafe(
            self._connection.notifies.put_nowait, "s"
        )


class PostgresJobStore(PostgresConnector):
    def __init__(self, *args, **kwargs):
        message = (
            "Use procrastinate.PostgresConnector(...) "
            "instead of procrastinate.PostgresJobStore(...), with the same arguments"
        )
        logger.warn(f"Deprecation Warning: {message}")
        warnings.warn(DeprecationWarning(message))
        super().__init__(*args, **kwargs)
