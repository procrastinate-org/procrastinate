import asyncio
import functools
import logging
from typing import Any, Callable, Coroutine, Dict, Iterable, List, Optional

import psycopg
import psycopg.errors
import psycopg.sql
import psycopg.types.json
import psycopg_pool
from psycopg.rows import DictRow, dict_row
from typing_extensions import LiteralString

from procrastinate import connector, exceptions, sql

logger = logging.getLogger(__name__)

LISTEN_TIMEOUT = 30.0

CoroutineFunction = Callable[..., Coroutine]


def wrap_exceptions(coro: CoroutineFunction) -> CoroutineFunction:
    """
    Wrap psycopg errors as connector exceptions.

    This decorator is expected to be used on coroutine functions only.
    """

    @functools.wraps(coro)
    async def wrapped(*args, **kwargs):
        try:
            return await coro(*args, **kwargs)
        except psycopg.errors.UniqueViolation as exc:
            raise exceptions.UniqueViolation(constraint_name=exc.diag.constraint_name)
        except psycopg.Error as exc:
            raise exceptions.ConnectorException from exc

    # Attaching a custom attribute to ease testability and make the
    # decorator more introspectable
    wrapped._exceptions_wrapped = True  # type: ignore
    return wrapped


class PsycopgConnector(connector.BaseAsyncConnector):
    def __init__(
        self,
        *,
        json_dumps: Optional[Callable] = None,
        json_loads: Optional[Callable] = None,
        **kwargs: Any,
    ):
        """
        Create a PostgreSQL connector using psycopg. The connector uses an
        ``psycopg_pool.AsyncConnectionPool``, which is created internally, or
        set into the connector by calling `App.open_async`.

        Note that if you want to use a ``psycopg_pool.AsyncNullConnectionPool``,
        you will need to initialize it yourself and pass it to the connector
        through the ``App.open_async`` method.

        All other arguments than ``json_dumps`` and ``json_loads`` are passed
        to ``psycopg_pool.AsyncConnectionPool`` (see psycopg documentation__).

        ``json_dumps`` and ``json_loads`` are used to configure new connections
        created by the pool with ``psycopg.types.json.set_json_dumps`` and
        ``psycopg.types.json.set_json_loads``.

        .. __: https://www.psycopg.org/psycopg3/docs/api/pool.html
               #psycopg_pool.AsyncConnectionPool

        Parameters
        ----------
        json_dumps :
            A function to serialize JSON objects to a string. If not provided,
            JSON objects will be serialized using psycopg's default JSON
            serializer.
        json_loads :
            A function to deserialize JSON objects from a string. If not
            provided, JSON objects will be deserialized using psycopg's default
            JSON deserializer.

        min_size : int
            Passed to psycopg, default set to 1 (same as aiopg).
        max_size : int
            Passed to psycopg, default set to 10 (same as aiopg).
        conninfo : ``Optional[str]``
            Passed to psycopg. Default is "" instead of None, which means if no
            argument is passed, it will connect to localhost:5432 instead of a
            Unix-domain local socket file.
        """
        self._pool: Optional[psycopg_pool.AsyncConnectionPool] = None
        self.json_dumps = json_dumps
        self._pool_externally_set = False
        self._pool_args = self._adapt_pool_args(kwargs, json_loads, json_dumps)
        self.json_loads = json_loads

    @staticmethod
    def _adapt_pool_args(
        pool_args: Dict[str, Any],
        json_loads: Optional[Callable],
        json_dumps: Optional[Callable],
    ) -> Dict[str, Any]:
        """
        Adapt the pool args for ``psycopg``, using sensible defaults for Procrastinate.
        """
        base_configure = pool_args.pop("configure", None)

        @wrap_exceptions
        async def configure(connection: psycopg.AsyncConnection[DictRow]):
            if base_configure:
                await base_configure(connection)

            if json_loads:
                psycopg.types.json.set_json_loads(json_loads, connection)

            if json_dumps:
                psycopg.types.json.set_json_dumps(json_dumps, connection)

        return {
            "conninfo": "",
            "min_size": 1,
            "max_size": 10,
            "kwargs": {
                "row_factory": dict_row,
            },
            "configure": configure,
            **pool_args,
        }

    @property
    def pool(
        self,
    ) -> psycopg_pool.AsyncConnectionPool[psycopg.AsyncConnection[DictRow]]:
        if self._pool is None:  # Set by open_async
            raise exceptions.AppNotOpen
        return self._pool

    async def open_async(
        self, pool: Optional[psycopg_pool.AsyncConnectionPool] = None
    ) -> None:
        """
        Instantiate the pool.

        pool :
            Optional pool. Procrastinate can use an existing pool. Connection parameters
            passed in the constructor will be ignored.
        """
        if self._pool:
            return

        if pool:
            self._pool_externally_set = True
            self._pool = pool
        else:
            self._pool = await self._create_pool(self._pool_args)

            await self._pool.open(wait=True)  # type: ignore

    @staticmethod
    @wrap_exceptions
    async def _create_pool(
        pool_args: Dict[str, Any]
    ) -> psycopg_pool.AsyncConnectionPool:
        return psycopg_pool.AsyncConnectionPool(
            **pool_args,
            # Not specifying open=False raises a warning and will be deprecated.
            # It makes sense, as we can't really make async I/Os in a constructor.
            open=False,
            # Enables a check that will ensure the connections returned when
            # using the pool are still alive. If they have been closed by the
            # database, they will be seamlessly replaced by a new connection.
            check=psycopg_pool.AsyncConnectionPool.check_connection,
        )

    @wrap_exceptions
    async def close_async(self) -> None:
        """
        Close the pool and awaits all connections to be released.
        """
        if not self._pool or self._pool_externally_set:
            return

        await self._pool.close()
        self._pool = None

    def _wrap_json(self, arguments: Dict[str, Any]):
        return {
            key: psycopg.types.json.Jsonb(value) if isinstance(value, dict) else value
            for key, value in arguments.items()
        }

    @wrap_exceptions
    async def execute_query_async(self, query: LiteralString, **arguments: Any) -> None:
        async with self.pool.connection() as connection:
            await connection.execute(query, self._wrap_json(arguments))

    @wrap_exceptions
    async def execute_query_one_async(
        self, query: LiteralString, **arguments: Any
    ) -> DictRow:
        async with self.pool.connection() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(query, self._wrap_json(arguments))

                result = await cursor.fetchone()

                if result is None:
                    raise exceptions.NoResult
                return result

    @wrap_exceptions
    async def execute_query_all_async(
        self, query: LiteralString, **arguments: Any
    ) -> List[DictRow]:
        async with self.pool.connection() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(query, self._wrap_json(arguments))
                return await cursor.fetchall()

    @wrap_exceptions
    async def listen_notify(
        self, event: asyncio.Event, channels: Iterable[str]
    ) -> None:
        # We need to acquire a dedicated connection, and use the listen
        # query
        if self.pool.max_size == 1:
            logger.warning(
                "Listen/Notify capabilities disabled because maximum pool size"
                "is set to 1",
                extra={"action": "listen_notify_disabled"},
            )
            return

        query_template = psycopg.sql.SQL(sql.queries["listen_queue"])

        while True:
            async with self.pool.connection() as connection:
                # autocommit is required for async connection notifies
                await connection.set_autocommit(True)

                for channel_name in channels:
                    query = query_template.format(
                        channel_name=psycopg.sql.Identifier(channel_name)
                    )
                    await connection.execute(query)
                # Initial set() lets caller know that we're ready to listen
                event.set()
                await self._loop_notify(event=event, connection=connection)

    @wrap_exceptions
    async def _loop_notify(
        self,
        event: asyncio.Event,
        connection: psycopg.AsyncConnection,
    ) -> None:
        # We'll leave this loop with a CancelledError, when we get cancelled

        while True:
            if connection.closed:
                return
            try:
                notifies = connection.notifies()
                async for _ in notifies:
                    event.set()
            except psycopg.OperationalError:
                break

    def __del__(self):
        pass
