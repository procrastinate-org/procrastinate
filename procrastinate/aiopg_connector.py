import asyncio
import logging
import warnings
from typing import Any, Callable, Dict, Iterable, List, Optional, NoReturn

import aiopg
import psycopg2.sql
from psycopg2.extras import Json, RealDictCursor

from procrastinate import connector, sql

logger = logging.getLogger(__name__)


class PostgresConnector(connector.BaseConnector):
    def __init__(
        self,
        dsn="",
        json_dumps: Optional[Callable] = None,
        json_loads: Optional[Callable] = None,
        **kwargs: Any,
    ):
        """
        All parameters except ``json_dumps`` and ``json_loads``
        are passed to :py:func:`aiopg.create_pool` (see the documentation__)

        .. __: https://aiopg.readthedocs.io/en/stable/core.html#aiopg.create_pool
        .. _psycopg2 doc: https://www.psycopg.org/docs/extras.html#json-adaptation

        Parameters
        ----------
        json_dumps:
            The JSON dumps function to use for serializing job arguments. Defaults to
            the function used by psycopg2. See the `psycopg2 doc`_.
        json_loads:
            The JSON loads function to use for deserializing job arguments. Defaults
            to the function used by psycopg2. See the `psycopg2 doc`_.

        """
        kwargs["dsn"] = dsn
        self._pool_parameters = kwargs
        self._pool: Optional[aiopg.pool] = None
        self.json_dumps = json_dumps
        self.json_loads = json_loads

    async def close_pool(self) -> None:
        if not self._pool:
            return

        self._pool.close()
        await self._pool.wait_closed()

    def _wrap_json(self, arguments: Dict[str, Any]):
        return {
            key: Json(value, dumps=self.json_dumps)
            if isinstance(value, dict)
            else value
            for key, value in arguments.items()
        }

    async def _get_pool(self) -> aiopg.Pool:
        if self._pool and not self._pool.closed:
            return self._pool

        # tell aiopg not to register adapters for hstore & json by default, as
        # those are registered at the module level and could overwrite previously
        # defined adapters
        kwargs = self._pool_parameters
        kwargs.setdefault("enable_json", False)
        kwargs.setdefault("enable_hstore", False)
        kwargs.setdefault("enable_uuid", False)
        if self.json_loads:

            async def on_connect(connection):
                psycopg2.extras.register_default_jsonb(
                    connection.raw, loads=self.json_loads
                )

            kwargs["on_connect"] = on_connect

        pool = await aiopg.create_pool(**kwargs)
        self._pool = pool
        return pool

    async def execute_query(self, query: str, **arguments: Any,) -> None:
        await self._execute_query(query=query, connection=None, **arguments)

    async def _execute_query(
        self,
        query: str,
        connection: Optional[aiopg.Connection] = None,
        **arguments: Any,
    ) -> None:
        # The private version of the method accepts an arbitrary connection
        pool = connection or await self._get_pool()
        # aiopg can work with psycopg2's cursor class
        with await pool.cursor(cursor_factory=RealDictCursor) as cursor:
            await cursor.execute(query, self._wrap_json(arguments))

    async def execute_query_one(self, query: str, **arguments: Any) -> Dict[str, Any]:
        pool = await self._get_pool()
        # aiopg can work with psycopg2's cursor class
        with await pool.cursor(cursor_factory=RealDictCursor) as cursor:
            await cursor.execute(query, self._wrap_json(arguments))

            return await cursor.fetchone()

    async def execute_query_all(
        self, query: str, **arguments: Any
    ) -> List[Dict[str, Any]]:
        pool = await self._get_pool()
        # aiopg can work with psycopg2's cursor class
        with await pool.cursor(cursor_factory=RealDictCursor) as cursor:
            await cursor.execute(query, self._wrap_json(arguments))

            return await cursor.fetchall()

    def make_dynamic_query(self, query: str, **identifiers: str) -> str:
        return psycopg2.sql.SQL(query).format(
            **{
                key: psycopg2.sql.Identifier(value)
                for key, value in identifiers.items()
            }
        )

    async def listen_notify(
        self, event: asyncio.Event, channels: Iterable[str]
    ) -> NoReturn:

        async with (await self._get_pool()).acquire() as connection:
            for channel_name in channels:
                await self._execute_query(
                    connection=connection,
                    query=self.make_dynamic_query(
                        query=sql.queries["listen_queue"], channel_name=channel_name
                    ),
                )

            while True:
                # We'll leave this loop with a CancelError, when we get cancelled
                await connection.notifies.get()
                event.set()


class PostgresJobStore(PostgresConnector):
    def __init__(self, *args, **kwargs):
        message = (
            "Use procrastinate.PostgresConnector(...) "
            "instead of procrastinate.PostgresJobStore(...), with the same arguments"
        )
        logger.warn(f"Deprecation Warning: {message}")
        warnings.warn(DeprecationWarning(message))
