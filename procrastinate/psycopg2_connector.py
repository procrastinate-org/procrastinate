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


def wrap_query_exceptions(func: Callable) -> Callable:
    """
    Detect "admin shutdown" errors and retry a number of times.

    This is to handle the case where the database connection (obtained from the pool)
    was actually closed by the server. In this case, pyscopg2 raises an AdminShutdown
    exception when the connection is used for issuing a query. What we do is retry when
    an AdminShutdown is raised, and until the maximum number of retries is reached.

    The number of retries is set to the pool maximum size plus one, to handle the case
    where the connections we have in the pool were all closed on the server side.
    """

    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        final_exc = None
        try:
            max_tries = args[0]._pool.maxconn + 1
        except Exception:
            max_tries = 1
        for _ in range(max_tries):
            try:
                return func(*args, **kwargs)
            except psycopg2.errors.AdminShutdown:
                continue
        raise exceptions.ConnectorException(
            "Could not get a valid connection after {} tries".format(max_tries)
        ) from final_exc

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

        This is used if you want your ``.defer()`` calls to be purely synchronous, not
        asynchronous with a sync wrapper. You may need this if your program is
        multi-threaded and doesn't handle async loops well
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
            ``App.open`` method.
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
        self._pool: Optional[psycopg2.pool.AbstractConnectionPool] = None
        self._pool_args = self._adapt_pool_args(kwargs)
        self._pool_externally_set = False

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

    def open(
        self, pool: Optional[psycopg2.pool.AbstractConnectionPool] = None,
    ) -> None:
        """
        Instantiate the pool.

        pool :
            Optional pool. Procrastinate can use an existing pool. Connection parameters
            passed in the constructor will be ignored.
        """

        if pool:
            self._pool_externally_set = True
            self._pool = pool
        else:
            self._pool = self._create_pool(self._pool_args)

    @staticmethod
    @wrap_exceptions
    def _create_pool(pool_args: Dict[str, Any]) -> psycopg2.pool.AbstractConnectionPool:
        return psycopg2.pool.ThreadedConnectionPool(**pool_args)

    @wrap_exceptions
    def close(self) -> None:
        """
        Close the pool
        """
        if self._pool and not self._pool.closed and not self._pool_externally_set:
            self._pool.closeall()

    @property
    def pool(self) -> psycopg2.pool.AbstractConnectionPool:
        if self._pool is None:  # Set by open
            raise exceptions.AppNotOpen
        return self._pool

    def _wrap_json(self, arguments: Dict[str, Any]):
        return {
            key: Json(value, dumps=self.json_dumps)
            if isinstance(value, dict)
            else value
            for key, value in arguments.items()
        }

    @contextlib.contextmanager
    def _connection(self) -> psycopg2.extensions.connection:
        # in case of an admin shutdown (Postgres error code 57P01) we do not
        # rollback the connection or put the connection back to the pool as
        # this will cause a psycopg2.InterfaceError exception
        connection = self.pool.getconn()
        try:
            yield connection
        except psycopg2.errors.AdminShutdown:
            raise
        except Exception:
            connection.rollback()
            self.pool.putconn(connection)
            raise
        else:
            connection.commit()
            self.pool.putconn(connection)

    @wrap_exceptions
    @wrap_query_exceptions
    def execute_query(self, query: str, **arguments: Any) -> None:
        with self._connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, self._wrap_json(arguments))

    @wrap_exceptions
    @wrap_query_exceptions
    def execute_query_one(self, query: str, **arguments: Any) -> Dict[str, Any]:
        with self._connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, self._wrap_json(arguments))
                return cursor.fetchone()

    @wrap_exceptions
    @wrap_query_exceptions
    def execute_query_all(self, query: str, **arguments: Any) -> Dict[str, Any]:
        with self._connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, self._wrap_json(arguments))
                return cursor.fetchall()
