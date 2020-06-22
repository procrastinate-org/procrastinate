import asyncio
import functools
import logging
from typing import Any, Callable, Coroutine, Dict, Iterable, List, Optional

import aiopg
import psycopg2
import psycopg2.errors
import psycopg2.sql
from psycopg2.extras import Json, RealDictCursor

from procrastinate import connector, exceptions, sql

logger = logging.getLogger(__name__)

LISTEN_TIMEOUT = 30.0

CoroutineFunction = Callable[..., Coroutine]


def wrap_exceptions(coro: CoroutineFunction) -> CoroutineFunction:
    """
    Wrap psycopg2 and aiopg errors as connector exceptions.

    This decorator is expected to be used on coroutine functions only.
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


def wrap_query_exceptions(coro: CoroutineFunction) -> CoroutineFunction:
    """
    Detect aiopg OperationalError's with a "server closed the connection unexpectedly"
    message and retry a number of times.

    This is to handle the case where the database connection (obtained from the pool)
    was actually closed by the server. In this case, aiopg raises an OperationalError
    with a "server closed the connection unexpectedly" message (and no pgcode) when the
    connection is used for issuing a query. What we do is retry when an OperationalError
    is raised, and until the maximum number of retries is reached.

    The number of retries is set to the pool maximum size plus one, to handle the case
    where the connections we have in the pool were all closed on the server side.
    """

    @functools.wraps(coro)
    async def wrapped(*args, **kwargs):
        final_exc = None
        try:
            max_tries = args[0]._pool.maxsize + 1
        except Exception:
            max_tries = 1
        for _ in range(max_tries):
            try:
                return await coro(*args, **kwargs)
            except psycopg2.errors.OperationalError as exc:
                if "server closed the connection unexpectedly" in str(exc):
                    final_exc = exc
                    continue
                raise exc
        raise exceptions.ConnectorException(
            "Could not get a valid connection after {} tries".format(max_tries)
        ) from final_exc

    return wrapped


class AiopgConnector(connector.BaseAsyncConnector):
    def __init__(
        self,
        *,
        json_dumps: Optional[Callable] = None,
        json_loads: Optional[Callable] = None,
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
            Passed to aiopg. If value is 1, then listen/notify feature will be
            deactivated.
        minsize : ``int``
            Passed to aiopg. Initial connections are not opened when the connector
            is created, but at first use of the pool.
        """
        self._pool: Optional[aiopg.Pool] = None
        self._pool_externally_set: bool = False
        self.json_dumps = json_dumps
        self.json_loads = json_loads
        self._pool_args = self._adapt_pool_args(kwargs, json_loads)
        self._lock: Optional[asyncio.Lock] = None

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

    def __del__(self):
        if self._pool and not self._pool_externally_set:
            # This one deserves a comment. Aiopg will close the free connections upon
            # __del__ but warns when doing so, so we'll be doing it ourselves. Plus,
            # there's no official sync method for closing all the connections in a pool.
            # This is a hack, and if something breaks around connection closing in the
            # future, it's a good idea to start looking here.
            self._pool.terminate()
            while self._pool._free:
                self._pool._free.popleft().close()

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

    def set_pool(self, pool: aiopg.Pool, *, _external: bool = True) -> None:
        """
        Set the connection pool. Raises an exception if the pool is already set.
        """

        if self._pool:
            raise exceptions.PoolAlreadySet
        self._pool_externally_set = _external
        self._pool = pool

    async def _get_pool(self) -> aiopg.Pool:
        if self._pool:
            return self._pool
        if not self._lock:
            self._lock = asyncio.Lock()
        async with self._lock:
            if not self._pool:
                self.set_pool(await self._create_pool(self._pool_args), _external=False)
        return self._pool

    # Pools and single connections do not exactly share their cursor API:
    # - connection.cursor() is an async context manager (async with)
    # - pool.cursor() is a coroutine returning a sync context manage (with await)
    # Because of this, it's easier to have 2 distinct methods for executing from
    # a pool or from a connection

    @wrap_exceptions
    @wrap_query_exceptions
    async def execute_query_async(self, query: str, **arguments: Any) -> None:
        pool = await self._get_pool()
        with await pool.cursor() as cursor:
            await cursor.execute(query, self._wrap_json(arguments))

    @wrap_exceptions
    @wrap_query_exceptions
    async def _execute_query_connection(
        self, query: str, connection: aiopg.Connection, **arguments: Any,
    ) -> None:
        async with connection.cursor() as cursor:
            await cursor.execute(query, self._wrap_json(arguments))

    @wrap_exceptions
    @wrap_query_exceptions
    async def execute_query_one_async(
        self, query: str, **arguments: Any
    ) -> Dict[str, Any]:
        pool = await self._get_pool()
        with await pool.cursor() as cursor:
            await cursor.execute(query, self._wrap_json(arguments))

            return await cursor.fetchone()

    @wrap_exceptions
    @wrap_query_exceptions
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
    ) -> None:
        pool = await self._get_pool()
        # We need to acquire a dedicated connection, and use the listen
        # query
        if pool.maxsize == 1:
            logger.warning(
                "Listen/Notify capabilities disabled because maximum pool size"
                "is set to 1",
                extra={"action": "listen_notify_disabled"},
            )
            return

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
