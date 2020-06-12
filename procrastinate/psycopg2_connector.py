import contextlib
import functools
import logging
from typing import Any, Callable, Dict, Optional

import psycopg2
import psycopg2.errors
import psycopg2.pool
from psycopg2.extras import Json, RealDictCursor

from procrastinate import connector, exceptions

logger = logging.getLogger(__name__)


def wrap_exceptions(func: Callable) -> Callable:
    """
    Wrap psycopg2 errors as connector exceptions
    This decorator is expected to be used on coroutine functions only
    """

    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except psycopg2.errors.UniqueViolation as exc:
            raise exceptions.UniqueViolation(constraint_name=exc.diag.constraint_name)
        except psycopg2.Error as exc:
            raise exceptions.ConnectorException from exc

    # Attaching a custom attribute to ease testability and make the
    # decorator more introspectable
    wrapped._exceptions_wrapped = True  # type: ignore
    return wrapped


class Psycopg2Connector(connector.BaseConnector):
    @wrap_exceptions
    def __init__(
        self,
        *,
        json_dumps: Optional[Callable] = None,
        json_loads: Optional[Callable] = None,
        pool: Optional[psycopg2.pool.ThreadedConnectionPool] = None,
        **kwargs: Any,
    ):
        """
        Synchronous connector based on a ``psycopg2.pool.ThreadedConnectionPool``.

        This is used if you want your ``.defer()`` calls to be pureley synchronous, not
        asynchronous with a sync wrapper. You may need this if your program is
        multithreaded and doesn't handle async loops well
        (see `discussion-sync-defer`).

        All other arguments than ``json_dumps`` are passed to
        :py:func:`ThreadedConnectionPool` (see psycopg2 documentation__), with default
        values that may differ from those of ``psycopg2`` (see a partial list of
        parameters below).

        .. _psycopg2 doc: https://www.psycopg.org/docs/extras.html#json-adaptation
        .. __: https://www.psycopg.org/docs/pool.html
               #psycopg2.pool.ThreadedConnectionPool

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
        pool :
            Optional pool. Procrastinate can use an existing pool. Additional parameters
            will be ignored.
        minconn : int
            Passed to psycopg2, default set to 1 (same as aiopg).
        maxconn : int
            Passed to psycopg2, default set to 10 (same as aiopg).
        dsn : ``Optional[str]``
            Passed to psycopg2. Default is "" instead of None, which means if no
            argument is passed, it will connect to localhost:5432 instead of a
            Unix-domain local socket file.
        cursor_factory : ``psycopg2.extensions.cursor``
            Passed to psycopg2. Default is ``psycopg2.extras.RealDictCursor``
            instead of standard cursor. There is no identified use case for changing
            this.
        """
        self.json_dumps = json_dumps
        self.json_loads = json_loads
        pool_args = self._adapt_pool_args(kwargs)
        self._pool = pool or psycopg2.pool.ThreadedConnectionPool(**pool_args)

    @staticmethod
    def _adapt_pool_args(pool_args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adapt the pool args for ``psycopg2``, using sensible defaults for Procrastinate.
        """
        final_args = {
            "minconn": 1,
            "maxconn": 10,
            "dsn": "",
            "cursor_factory": RealDictCursor,
        }
        final_args.update(pool_args)
        return final_args

    @wrap_exceptions
    def close(self) -> None:
        """
        Close the pool
        """
        self._pool.closeall()

    def _wrap_json(self, arguments: Dict[str, Any]):
        return {
            key: Json(value, dumps=self.json_dumps)
            if isinstance(value, dict)
            else value
            for key, value in arguments.items()
        }

    @contextlib.contextmanager
    def _connection(self) -> psycopg2.extensions.connection:
        try:
            with self._pool.getconn() as connection:
                yield connection
        finally:
            self._pool.putconn(connection)

    @wrap_exceptions
    def execute_query(self, query: str, **arguments: Any) -> None:
        with self._connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, self._wrap_json(arguments))

    @wrap_exceptions
    def execute_query_one(self, query: str, **arguments: Any) -> Dict[str, Any]:
        with self._connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, self._wrap_json(arguments))
                return cursor.fetchone()
