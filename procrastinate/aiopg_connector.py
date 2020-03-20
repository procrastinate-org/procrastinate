import asyncio
import logging
import warnings
from typing import Any, Callable, Dict, Iterable, List, NoReturn, Optional

import aiopg
import psycopg2.sql
from psycopg2.extras import Json, RealDictCursor

from procrastinate import connector, sql, utils

logger = logging.getLogger(__name__)


@utils.add_sync_api
class PostgresConnector(connector.BaseConnector):
    def __init__(
        self,
        pool: aiopg.Pool,
        json_dumps: Optional[Callable] = None,
        json_loads: Optional[Callable] = None,
    ):
        """
        The pool connections are expected to have jsonb adapters.

        See parameter details in :py:func:`PostgresConnector.create_with_pool`.

        Parameters
        ----------
        pool:
            An aiopg pool, either externally configured or passed by
            :py:func:`PostgresConnector.create_with_pool`.

        """
        self._pool = pool
        self.json_dumps = json_dumps
        self.json_loads = json_loads

    async def close_async(self) -> None:
        """
        Closes the pool and awaits all connections to be released.
        """
        self._pool.close()
        await self._pool.wait_closed()

    def _wrap_json(self, arguments: Dict[str, Any]):
        return {
            key: Json(value, dumps=self.json_dumps)
            if isinstance(value, dict)
            else value
            for key, value in arguments.items()
        }

    @classmethod
    async def create_with_pool_async(
        cls,
        json_dumps: Optional[Callable] = None,
        json_loads: Optional[Callable] = None,
        **kwargs,
    ) -> aiopg.Pool:
        """
        Creates a connector, and its connection pool, using the provided parameters.
        All additional parameters will be used to create a
        :py:func:`aiopg.Pool` (see the documentation__), sometimes with a different
        default value.

        When using this method, you explicitely take the responsibility for opening the
        pool. It's your responsibility to call
        :py:func:`procrastinate.PostgresConnector.close` or
        :py:func:`procrastinate.PostgresConnector.close_async` to close connections
        when your process ends.

        .. __: https://aiopg.readthedocs.io/en/stable/core.html#aiopg.create_pool
        .. _psycopg2 doc: https://www.psycopg.org/docs/extras.html#json-adaptation

        json_dumps:
            The JSON dumps function to use for serializing job arguments. Defaults to
            the function used by psycopg2. See the `psycopg2 doc`_.
        json_loads:
            The JSON loads function to use for deserializing job arguments. Defaults
            to the function used by psycopg2. See the `psycopg2 doc`_. Unused if pool
            is passed.
        dsn (Optional[str]):
            Passed to aiopg. Default is "" instead of None, which means if no argument
            is passed, it will connect to localhost:5432 instead of a Unix-domain
            local socket file.
        enable_json (bool):
            Passed to aiopg. Default is False instead of True to avoid messing with
            the global state.
        enable_hstore (bool):
            Passed to aiopg. Default is False instead of True to avoid messing with
            the global state.
        enable_uuid (bool):
            Passed to aiopg. Default is False instead of True to avoid messing with
            the global state.
        cursor_factory (psycopg2.extensions.cursor):
            Passed to aiopg. Default is :py:class:`psycopg2.extras.RealDictCursor`
            instead of standard cursor. There is no identified use case for changing
            this.
        maxsize (int):
            Passed to aiopg. Cannot be lower than 2, otherwise worker won't be
            functionning normally (one connection for listen/notify, one for executing
            tasks).
        """
        base_on_connect = kwargs.pop("on_connect", None)

        async def on_connect(connection):
            if base_on_connect:
                base_on_connect(connection)
            if json_loads:
                psycopg2.extras.register_default_jsonb(connection.raw, loads=json_loads)

        defaults = {
            "dsn": "",
            "enable_json": False,
            "enable_hstore": False,
            "enable_uuid": False,
            "on_connect": on_connect,
            "cursor_factory": RealDictCursor,
        }
        defaults.update(kwargs)

        if "maxsize" in kwargs:
            kwargs["maxsize"] = max(2, kwargs["maxsize"])

        pool = await aiopg.create_pool(**defaults)

        return cls(pool=pool, json_dumps=json_dumps, json_loads=json_loads)

    # Pools and single connections do not exactly share their cursor API:
    # - connection.cursor() is an async context manager (async with)
    # - pool.cursor() is a coroutine returning a sync context manage (with await)
    # Because of this, it's easier to have 2 distinct methods for executing from
    # a pool or from a connection

    async def execute_query(self, query: str, **arguments: Any) -> None:
        with await self._pool.cursor() as cursor:
            await cursor.execute(query, self._wrap_json(arguments))

    async def _execute_query_connection(
        self, query: str, connection: aiopg.Connection, **arguments: Any,
    ) -> None:
        async with connection.cursor() as cursor:
            await cursor.execute(query, self._wrap_json(arguments))

    async def execute_query_one(self, query: str, **arguments: Any) -> Dict[str, Any]:
        with await self._pool.cursor() as cursor:
            await cursor.execute(query, self._wrap_json(arguments))

            return await cursor.fetchone()

    async def execute_query_all(
        self, query: str, **arguments: Any
    ) -> List[Dict[str, Any]]:

        with await self._pool.cursor() as cursor:
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
        self,
        channels: Iterable[str],
        notify_event: asyncio.Event,
        listen_event: Optional[asyncio.Event],
    ) -> NoReturn:
        # We need to acquire a dedicated connection, and use the listen
        # query
        async with self._pool.acquire() as connection:
            for channel_name in channels:
                await self._execute_query_connection(
                    connection=connection,
                    query=self.make_dynamic_query(
                        query=sql.queries["listen_queue"], channel_name=channel_name
                    ),
                )
            if listen_event:
                listen_event.set()
            # We'll leave this loop with a CancelledError, when we get cancelled
            while True:
                # TODO: because of https://github.com/aio-libs/aiopg/issues/249,
                # we could get stuck in here forever if the connection closes.
                # Maybe we should set a timeout and if connection is closed, reopen
                # a new one.
                await connection.notifies.get()
                notify_event.set()


def PostgresJobStore(*args, **kwargs):
    message = (
        "Use procrastinate.PostgresConnector(...) "
        "instead of procrastinate.PostgresJobStore(...), with the same arguments"
    )
    logger.warn(f"Deprecation Warning: {message}")
    warnings.warn(DeprecationWarning(message))
    return PostgresConnector.create_with_pool(*args, **kwargs)
