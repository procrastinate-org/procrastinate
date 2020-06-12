import asyncio
import functools
import logging
from typing import Any, Callable, Coroutine, Dict, Iterable, List, NoReturn, Optional

import aiopg
import psycopg2
import psycopg2.errors
import psycopg2.sql
from psycopg2.extras import Json, RealDictCursor

from procrastinate import connector, exceptions, psycopg2_connector, sql

logger = logging.getLogger(__name__)

LISTEN_TIMEOUT = 30.0

CoroutineFunction = Callable[..., Coroutine]


def wrap_exceptions(coro: CoroutineFunction) -> CoroutineFunction:
    """
    Wrap psycopg2 and aiopg errors as connector exceptions
    This decorator is expected to be used on coroutine functions only
    """

    @functools.wraps(coro)
    async def wrapped(*args, **kwargs):
        try:
            return await coro(*args, **kwargs)
        except psycopg2.errors.UniqueViolation as exc:
            raise exceptions.UniqueViolation(constraint_name=exc.diag.constraint_name)
        except psycopg2.Error as exc:
            raise exceptions.ConnectorException from exc

    # Attaching a custom attribute to ease testability and make the
    # decorator more introspectable
    wrapped._exceptions_wrapped = True  # type: ignore
    return wrapped


class AiopgConnector(connector.BaseAsyncConnector):
    def __init__(
        self,
        *,
        json_dumps: Optional[Callable] = None,
        json_loads: Optional[Callable] = None,
        real_sync_defer: bool = False,
        **kwargs: Any,
    ):
        """
        Create a PostgreSQL connector using aiopg. The connector uses an ``aiopg.Pool``,
        which is either created automatically upon first use, or set through the
        `AiopgConnector.set_pool` method.

        All other arguments than ``json_dumps`` and ``json_loads`` are passed to
        :py:func:`aiopg.create_pool` (see aiopg documentation__), with default values
        that may differ from those of ``aiopg`` (see the list of parameters below).

        .. _psycopg2 doc: https://www.psycopg.org/docs/extras.html#json-adaptation
        .. __: https://aiopg.readthedocs.io/en/stable/core.html#aiopg.create_pool

        Parameters
        ----------
        json_dumps :
            The JSON dumps function to use for serializing job arguments. Defaults to
            the function used by psycopg2. See the `psycopg2 doc`_.
        json_loads :
            The JSON loads function to use for deserializing job arguments. Defaults
            to the function used by psycopg2. See the `psycopg2 doc`_. Unused if the
            pool is externally created and set into the connector through the
            `AiopgConnector.set_pool` method.
        real_sync_defer :
            If a synchronous call to a defer operation is issued, whether to call a
            really synchronous psycopg2 implementation (``True``) which will use its own
            connection pool, or a synchronous wrapper around this asynchronous
            connector, which may not play as nicely with multithreaded programs but will
            use connections from this connector's pool (``False``)(see
            `discussion-sync-defer`).
        dsn : ``Optional[str]``
            Passed to aiopg. Default is "" instead of None, which means if no argument
            is passed, it will connect to localhost:5432 instead of a Unix-domain
            local socket file.
        enable_json : ``bool``
            Passed to aiopg. Default is False instead of True to avoid messing with
            the global state.
        enable_hstore: ``bool``
            Passed to aiopg. Default is False instead of True to avoid messing with
            the global state.
        enable_uuid : ``bool``
            Passed to aiopg. Default is False instead of True to avoid messing with
            the global state.
        cursor_factory : ``psycopg2.extensions.cursor``
            Passed to aiopg. Default is ``psycopg2.extras.RealDictCursor``
            instead of standard cursor. There is no identified use case for changing
            this.
        maxsize : ``int``
            Passed to aiopg. Cannot be lower than 2, otherwise worker won't be
            functioning normally (one connection for listen/notify, one for executing
            tasks).
        minsize : ``int``
            Passed to aiopg. Initial connections are not opened when the connector
            is created, but at first use of the pool.
        """
        self._pool: Optional[aiopg.Pool] = None
        self.json_dumps = json_dumps
        self.json_loads = json_loads
        self._pool_args = self._adapt_pool_args(kwargs, json_loads)
        self._lock: Optional[asyncio.Lock] = None
        self._sync_connector: Optional[psycopg2_connector.Psycopg2Connector] = None
        self.real_sync_defer = real_sync_defer

    @staticmethod
    def _adapt_pool_args(
        pool_args: Dict[str, Any], json_loads: Optional[Callable]
    ) -> Dict[str, Any]:
        """
        Adapt the pool args for ``aiopg``, using sensible defaults for Procrastinate.
        """
        base_on_connect = pool_args.pop("on_connect", None)

        @wrap_exceptions
        async def on_connect(connection):
            if base_on_connect:
                await base_on_connect(connection)
            if json_loads:
                psycopg2.extras.register_default_jsonb(connection.raw, loads=json_loads)

        final_args = {
            "dsn": "",
            "enable_json": False,
            "enable_hstore": False,
            "enable_uuid": False,
            "on_connect": on_connect,
            "cursor_factory": RealDictCursor,
        }
        if "maxsize" in pool_args:
            pool_args["maxsize"] = max(2, pool_args["maxsize"])

        final_args.update(pool_args)
        return final_args

    @wrap_exceptions
    async def close_async(self) -> None:
        """
        Close the pool and awaits all connections to be released.
        """
        if self._pool:
            self._pool.close()
            await self._pool.wait_closed()
            self._pool = None
        if self._sync_connector:
            # This is not an async call but hopefully at this point, it's ok.
            self._sync_connector.close()

    def _wrap_json(self, arguments: Dict[str, Any]):
        return {
            key: Json(value, dumps=self.json_dumps)
            if isinstance(value, dict)
            else value
            for key, value in arguments.items()
        }

    @staticmethod
    @wrap_exceptions
    async def _create_pool(pool_args: Dict[str, Any]) -> aiopg.Pool:
        return await aiopg.create_pool(**pool_args)

    def set_pool(self, pool: aiopg.Pool) -> None:
        """
        Set the connection pool. Raises an exception if the pool is already set.
        """
        if self._pool:
            raise exceptions.PoolAlreadySet
        self._pool = pool

    async def _get_pool(self) -> aiopg.Pool:
        if self._pool:
            return self._pool
        if not self._lock:
            self._lock = asyncio.Lock()
        async with self._lock:
            if not self._pool:
                self.set_pool(await self._create_pool(self._pool_args))
        return self._pool

    # Pools and single connections do not exactly share their cursor API:
    # - connection.cursor() is an async context manager (async with)
    # - pool.cursor() is a coroutine returning a sync context manage (with await)
    # Because of this, it's easier to have 2 distinct methods for executing from
    # a pool or from a connection

    @wrap_exceptions
    async def execute_query_async(self, query: str, **arguments: Any) -> None:
        pool = await self._get_pool()
        with await pool.cursor() as cursor:
            await cursor.execute(query, self._wrap_json(arguments))

    @wrap_exceptions
    async def _execute_query_connection(
        self, query: str, connection: aiopg.Connection, **arguments: Any,
    ) -> None:
        async with connection.cursor() as cursor:
            await cursor.execute(query, self._wrap_json(arguments))

    @wrap_exceptions
    async def execute_query_one_async(
        self, query: str, **arguments: Any
    ) -> Dict[str, Any]:
        pool = await self._get_pool()
        with await pool.cursor() as cursor:
            await cursor.execute(query, self._wrap_json(arguments))

            return await cursor.fetchone()

    @wrap_exceptions
    async def execute_query_all_async(
        self, query: str, **arguments: Any
    ) -> List[Dict[str, Any]]:
        pool = await self._get_pool()
        with await pool.cursor() as cursor:
            await cursor.execute(query, self._wrap_json(arguments))

            return await cursor.fetchall()

    def _make_dynamic_query(self, query: str, **identifiers: str) -> str:
        return psycopg2.sql.SQL(query).format(
            **{
                key: psycopg2.sql.Identifier(value)
                for key, value in identifiers.items()
            }
        )

    @wrap_exceptions
    async def listen_notify(
        self, event: asyncio.Event, channels: Iterable[str]
    ) -> NoReturn:
        pool = await self._get_pool()
        # We need to acquire a dedicated connection, and use the listen
        # query
        while True:
            async with pool.acquire() as connection:
                for channel_name in channels:
                    await self._execute_query_connection(
                        connection=connection,
                        query=self._make_dynamic_query(
                            query=sql.queries["listen_queue"], channel_name=channel_name
                        ),
                    )
                # Initial set() lets caller know that we're ready to listen
                event.set()
                await self._loop_notify(event=event, connection=connection)

    @wrap_exceptions
    async def _loop_notify(
        self,
        event: asyncio.Event,
        connection: aiopg.Connection,
        timeout: float = LISTEN_TIMEOUT,
    ) -> None:
        # We'll leave this loop with a CancelledError, when we get cancelled
        while True:
            # because of https://github.com/aio-libs/aiopg/issues/249,
            # we could get stuck in here forever if the connection closes.
            # That's why we need timeout and if connection is closed, reopen
            # a new one.
            if connection.closed:
                return
            try:
                await asyncio.wait_for(connection.notifies.get(), timeout)
            except asyncio.TimeoutError:
                continue

            event.set()

    def get_sync_connector(self) -> connector.BaseConnector:
        if not self.real_sync_defer:
            return super().get_sync_connector()

        if self._sync_connector:
            return self._sync_connector

        pool_args = self._pool_args.copy()
        pool_args["minconn"] = pool_args.pop("minsize", 1)
        pool_args["maxconn"] = pool_args.pop("maxsize", 10)
        pool_args.pop("enable_json", None)
        pool_args.pop("enable_hstore", None)
        pool_args.pop("enable_uuid", None)
        pool_args.pop("on_connect", None)
        self._sync_connector = psycopg2_connector.Psycopg2Connector(
            json_dumps=self.json_dumps, **pool_args
        )
        return self._sync_connector
