import logging
import warnings
from typing import Any, Callable, Dict, List, Optional

import aiopg
import psycopg2.sql
from psycopg2.extras import Json, RealDictCursor

from procrastinate import connector, utils

logger = logging.getLogger(__name__)


@utils.add_sync_api
class PostgresConnector(connector.BaseConnector):
    def __init__(
        self,
        pool: aiopg.Pool,
        socket_timeout: float = connector.SOCKET_TIMEOUT,
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
        self.socket_timeout = socket_timeout
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
        socket_timeout: float = connector.SOCKET_TIMEOUT,
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

        pool = await aiopg.create_pool(**defaults)

        return cls(
            pool=pool,
            socket_timeout=socket_timeout,
            json_dumps=json_dumps,
            json_loads=json_loads,
        )

    async def execute_query(self, query: str, **arguments: Any) -> None:
        with await self._pool.cursor() as cursor:
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


def PostgresJobStore(*args, **kwargs):
    message = (
        "Use procrastinate.PostgresConnector(...) "
        "instead of procrastinate.PostgresJobStore(...), with the same arguments"
    )
    logger.warn(f"Deprecation Warning: {message}")
    warnings.warn(DeprecationWarning(message))
    return PostgresConnector.create_with_pool(*args, **kwargs)
