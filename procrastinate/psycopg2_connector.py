from typing import Any, Dict, List

import psycopg2
from psycopg2 import extras
from psycopg2 import sql as psycopg2_sql
from psycopg2.extras import Json, RealDictCursor

from procrastinate import store


def get_connection(*args, **kwargs) -> psycopg2._psycopg.connection:
    return psycopg2.connect(*args, **kwargs)


def init_pg_extensions() -> None:
    psycopg2.extensions.register_adapter(dict, extras.Json)


def wrap_json(arguments: Dict[str, Any]):
    return {
        key: Json(value) if isinstance(value, dict) else value
        for key, value in arguments.items()
    }


def execute_query(
    connection: psycopg2._psycopg.connection, query: str, **arguments: Any
) -> None:
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(query, wrap_json(arguments))
            connection.commit()


def execute_query_one(
    connection: psycopg2._psycopg.connection, query: str, **arguments: Any
) -> Dict[str, Any]:
    with connection:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, wrap_json(arguments))
            connection.commit()
            return cursor.fetchone()


def execute_query_all(
    connection: psycopg2._psycopg.connection, query: str, **arguments: Any
) -> List[Dict[str, Any]]:
    with connection:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, wrap_json(arguments))
            connection.commit()
            return cursor.fetchall()


def make_dynamic_query(query: str, **identifiers: str) -> str:
    return psycopg2_sql.SQL(query).format(
        **{key: psycopg2_sql.Identifier(value) for key, value in identifiers.items()}
    )


init_pg_extensions()


class PostgresJobStore(store.BaseJobStore):
    """
    Uses `psycopg2` to establish a synchronous
    connection to a Postgres database.
    """

    def __init__(self, socket_timeout: float = store.SOCKET_TIMEOUT, **kwargs: Any):
        """
        All parameters except `socket_timeout` are passed to
        :py:func:`psycopg2.connect` (see the documentation_)

        .. _documentation: http://initd.org/psycopg/docs/module.html#psycopg2.connect

        Parameters
        ----------
        socket_timeout:
            This parameter should generally not be changed.
            It indicates how long procrastinate waits (in seconds) between
            renewing the socket `select` calls when waiting for tasks.
            The shorter the timeout, the more `select` calls it does.
            The longer the timeout, the longer the server will wait idle if, for
            some reason, the postgres LISTEN call doesn't work.
        """
        self.connection = get_connection(**kwargs)
        super().__init__(socket_timeout=socket_timeout)

    def get_connection(self):
        return self.connection

    def execute_query(self, query: str, **arguments: Any) -> None:
        execute_query(self.connection, query=query, **arguments)

    def execute_query_one(self, query: str, **arguments: Any) -> Dict[str, Any]:
        return execute_query_one(self.connection, query=query, **arguments)

    def execute_query_all(self, query: str, **arguments: Any) -> List[Dict[str, Any]]:
        return execute_query_all(self.connection, query=query, **arguments)

    def make_dynamic_query(self, query: str, **identifiers: str) -> str:
        return make_dynamic_query(query=query, **identifiers)
