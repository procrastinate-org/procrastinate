from typing import Any, Callable, Coroutine, Dict, Iterable, List, Optional

import asyncpg

from procrastinate import connector, exceptions, sql


def wrap_exceptions(coro: CoroutineFunction) -> CoroutineFunction:
    """
    Wrap asyncpg errors as connector exceptions.

    This decorator is expected to be used on coroutine functions only.
    """

    @functools.wraps(coro)
    async def wrapped(*args, **kwargs):
        try:
            return await coro(*args, **kwargs)
        except asyncpg.errors.UniqueViolation as exc:
            raise exceptions.UniqueViolation(constraint_name=exc.diag.constraint_name)
        except asyncpg.Error as exc:
            raise exceptions.ConnectorException from exc

    # Attaching a custom attribute to ease testability and make the
    # decorator more introspectable
    wrapped._exceptions_wrapped = True  # type: ignore
    return wrapped


class AsyncpgQueryConverter:
    def __init__(self):
        self.order = []

    def __getitem__(self, key):
        self.order.append(key)
        return f"${len(self.order)}"

    def convert_args(self, args):
        return tuple(args[e] for e in self.order)


class AsyncpgConnector(connector.BaseAsyncConnector):
    def __init__(
        self,
        *,
        json_dumps: Optional[Callable] = None,
        json_loads: Optional[Callable] = None,
        **kwargs: Any,
    ):
        """
        Create a PostgreSQL connector using asyncpg. The connector uses an ``asyncpg.Pool``, either
        created internally or specified when initializing the `AsyncpgConnector` in the pool parameter.

        All other arguments than ``json_dumps`` and ``json_loads`` are passed to
        :py:func:`asyncpg.create_pool` (see asyncpg documentation__), with default values
        that may differ from those of ``asyncpg`` (see the list of parameters below).

        .. __: https://magicstack.github.io/asyncpg/current/api/index.html#asyncpg.pool.create_pool

        Parameters
        ----------
        json_dumps :
            The JSON dumps function to use for serializing job arguments. Defaults to
            the function used by psycopg2. See the `psycopg2 doc`_.
        json_loads :
            The JSON loads function to use for deserializing job arguments. Defaults
            to the function used by psycopg2. See the `psycopg2 doc`_. Unused if the
            pool is externally created and set into the connector through the
            ``App.open_async`` method.
        """
        self._pool: Optional[asyncpg.Pool] = None
        self._pool_externally_set: bool = False
        self.json_dumps = json_dumps
        self.json_loads = json_loads
        self._pool_args = kwargs
        self._lock: Optional[asyncio.Lock] = None

    @property
    def pool(self) -> aiopg.Pool:
        if self._pool is None:  # Set by open_async
            raise exceptions.AppNotOpen
        return self._pool

    async def open_async(self, pool: Optional[aiopg.Pool] = None) -> None:
        if self._pool:
            return
        if pool:
            self._pool_externally_set = True
            self._pool = pool
        else:
            self._pool = await self._create_pool(
                self._pool_args, self.json_dumps, self.json_loads
            )

    @staticmethod
    @wrap_exceptions
    async def _create_pool(
        pool_args: Dict[str, Any], json_dumps, json_loads
    ) -> aiopg.Pool:
        extra_init = pool_args.get("init", None)

        async def init(conn):
            conn.set_type_codec("json", encoder=json_dumps, decoder=json_loads)
            if extra_init:
                await extra_init(conn)

        return await asyncpg.create_pool(init=init, **pool_args)

    @wrap_exceptions
    async def close_async(self) -> None:
        """
        Close the pool and awaits all connections to be released.
        """

        if not self._pool or self._pool_externally_set:
            return
        await self._pool.close()
        self._pool = None

    async def __del__(self):
        if self._pool and not self._pool_externally_set:
            # Consider https://docs.python.org/3/library/asyncio-task.html#asyncio.wait_for
            await self._pool.close()

    async def execute_query_async(self, query: str, **arguments: Any) -> None:
        converter = AsyncpgQueryConverter()
        converted_query = query % converter

        with self.pool.acquire() as conn:
            args = converter.convert_args(arguments)
            await conn.execute(converted_query, *args)

    async def execute_query_one_async(
        self, query: str, **arguments: Any
    ) -> Dict[str, Any]:
        converter = AsyncpgQueryConverter()
        converted_query = query % converter

        with self.pool.acquire() as conn:
            args = converter.convert_args(arguments)
            row_record = await conn.fetchrow(converted_query, *args)
            return {key: value for key, value in row_record.items()}

    async def execute_query_all_async(
        self, query: str, **arguments: Any
    ) -> List[Dict[str, Any]]:
        converter = AsyncpgQueryConverter()
        converted_query = query % converter

        with self.pool.acquire() as conn:
            args = converter.convert_args(arguments)
            # consider using a cursor instead
            rows = await conn.fetch(converted_query, *args)

            return list(
                [
                    {key: value for key, value in row_record.items()}
                    for row_record in rows
                ]
            )

    async def listen_notify(
        self, event: asyncio.Event, channels: Iterable[str]
    ) -> None:
        async def listen_callback(conn, pid, channel, payload):
            event.set()

        async with self.pool.acquire() as conn:
            for channel in channels:
                await conn.add_listener(channel, listen_callback)
