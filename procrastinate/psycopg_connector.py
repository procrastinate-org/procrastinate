from __future__ import annotations

import asyncio
import contextlib
import functools
import logging
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncIterator,
    Callable,
    Coroutine,
    Iterable,
    TypeVar,
    cast,
)

from typing_extensions import LiteralString, ParamSpec

from procrastinate import connector, exceptions, sql, sync_psycopg_connector, utils

if TYPE_CHECKING:
    import psycopg
    import psycopg.errors
    import psycopg.rows
    import psycopg.sql
    import psycopg.types.json
    import psycopg_pool
else:
    psycopg, *_ = utils.import_or_wrapper(
        "psycopg",
        "psycopg.errors",
        "psycopg.rows",
        "psycopg.sql",
        "psycopg.types.json",
    )
    (psycopg_pool,) = utils.import_or_wrapper("psycopg_pool")


logger = logging.getLogger(__name__)

T = TypeVar("T")
P = ParamSpec("P")


def wrap_exceptions(
    coro: Callable[P, Coroutine[None, Any, T]],
) -> Callable[P, Coroutine[None, Any, T]]:
    """
    Wrap psycopg errors as connector exceptions.

    This decorator is expected to be used on coroutine functions only.
    """

    @functools.wraps(coro)
    async def wrapped(*args: P.args, **kwargs: P.kwargs) -> T:
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
        json_dumps: Callable | None = None,
        json_loads: Callable | None = None,
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
        """
        self._async_pool: psycopg_pool.AsyncConnectionPool | None = None
        self._pool_externally_set: bool = False
        self._json_loads = json_loads
        self._json_dumps = json_dumps
        self._pool_args = kwargs
        self._sync_connector: connector.BaseConnector | None = None

    def get_sync_connector(self) -> connector.BaseConnector:
        if self._async_pool:
            return self
        if self._sync_connector is None:
            logger.debug(
                "PsycopgConnector used synchronously before being opened. "
                "Creating a SyncPsycopgConnector."
            )
            self._sync_connector = sync_psycopg_connector.SyncPsycopgConnector(
                json_dumps=self._json_dumps,
                json_loads=self._json_loads,
                **self._pool_args,
            )
        return self._sync_connector

    @property
    def pool(
        self,
    ) -> psycopg_pool.AsyncConnectionPool:
        if self._async_pool is None:  # Set by open_async
            raise exceptions.AppNotOpen
        return self._async_pool

    async def open_async(
        self, pool: psycopg_pool.AsyncConnectionPool | None = None
    ) -> None:
        """
        Instantiate the pool.

        pool :
            Optional pool. Procrastinate can use an existing pool. Connection parameters
            passed in the constructor will be ignored.
        """
        if self._async_pool:
            return

        if self._sync_connector is not None:
            logger.debug("Closing automatically created SyncPsycopgConnector.")
            await utils.sync_to_async(self._sync_connector.close)
            self._sync_connector = None

        if pool:
            self._pool_externally_set = True
            self._async_pool = pool
        else:
            self._async_pool = await self._create_pool(self._pool_args)

            await self._async_pool.open(wait=True)  # type: ignore

    @staticmethod
    @wrap_exceptions
    async def _create_pool(
        pool_args: dict[str, Any],
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
        if not self._async_pool or self._pool_externally_set:
            return

        await self._async_pool.close()
        self._async_pool = None

    def _wrap_json(self, arguments: dict[str, Any]):
        return {
            key: psycopg.types.json.Jsonb(value) if isinstance(value, dict) else value
            for key, value in arguments.items()
        }

    @contextlib.asynccontextmanager
    async def _get_cursor(self) -> AsyncIterator[psycopg.AsyncCursor]:
        async with self.pool.connection() as connection:
            async with connection.cursor(row_factory=psycopg.rows.dict_row) as cursor:
                if self._json_loads:
                    psycopg.types.json.set_json_loads(
                        loads=self._json_loads, context=cursor
                    )

                if self._json_dumps:
                    psycopg.types.json.set_json_dumps(
                        dumps=self._json_dumps, context=cursor
                    )
                yield cursor

    @wrap_exceptions
    async def execute_query_async(self, query: LiteralString, **arguments: Any) -> None:
        async with self._get_cursor() as cursor:
            await cursor.execute(query, self._wrap_json(arguments))

    @wrap_exceptions
    async def execute_query_one_async(
        self, query: LiteralString, **arguments: Any
    ) -> dict[str, Any]:
        async with self._get_cursor() as cursor:
            await cursor.execute(query, self._wrap_json(arguments))

            result = await cursor.fetchone()

            if result is None:
                raise exceptions.NoResult
            return result

    @wrap_exceptions
    async def execute_query_all_async(
        self, query: LiteralString, **arguments: Any
    ) -> list[dict[str, Any]]:
        async with self._get_cursor() as cursor:
            await cursor.execute(query, self._wrap_json(arguments))

            return await cursor.fetchall()

    def _make_dynamic_query(
        self,
        query: LiteralString,
        **identifiers: str,
    ) -> psycopg.sql.Composed:
        return psycopg.sql.SQL(query).format(
            **{key: psycopg.sql.Identifier(value) for key, value in identifiers.items()}
        )

    @wrap_exceptions
    async def listen_notify(
        self, event: asyncio.Event, channels: Iterable[str]
    ) -> None:
        while True:
            async with await self.pool.connection_class.connect(
                self.pool.conninfo, **self.pool.kwargs, autocommit=True
            ) as connection:
                connection = cast(psycopg.AsyncConnection, connection)
                for channel_name in channels:
                    await connection.execute(
                        query=self._make_dynamic_query(
                            query=sql.queries["listen_queue"],
                            channel_name=channel_name,
                        ),
                    )
                # Initial set() lets caller know that we're ready to listen
                event.set()
                await self._loop_notify(event=event, connection=connection)

    @wrap_exceptions
    async def _loop_notify(
        self,
        event: asyncio.Event,
        connection: psycopg.AsyncConnection,
        timeout: float = connector.LISTEN_TIMEOUT,
    ) -> None:
        # We'll leave this loop with a CancelledError, when we get cancelled

        while True:
            try:
                async for _ in utils.gen_with_timeout(
                    aiterable=connection.notifies(),
                    timeout=timeout,
                    raise_timeout=False,
                ):
                    event.set()

                await connection.execute("SELECT 1")
            except psycopg.OperationalError:
                # Connection is dead, we need to reconnect
                break
