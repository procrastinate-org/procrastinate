import functools
import json
import logging
import select
from typing import Any, Callable, Dict, Iterable, List, Optional, Set

import psycopg2
from django.db import DatabaseError
from django.db import connection as django_connection
from django.utils.connection import ConnectionProxy
from psycopg2 import errors as psycopg_errors
from psycopg2._json import JSONB_OID
from psycopg2.extensions import connection as postgres_conn
from psycopg2.extras import Json

from procrastinate import connector, exceptions, sql

logger = logging.getLogger(__name__)

LISTEN_TIMEOUT = 30.0


def wrap_exceptions(func: Callable) -> Callable:
    """
    Wrap django errors as connector exceptions.
    """

    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except DatabaseError as exc:
            psycopg_err = exc.__cause__
            if isinstance(psycopg_err, psycopg_errors.UniqueViolation):
                raise exceptions.UniqueViolation(
                    constraint_name=psycopg_err.diag.constraint_name
                )
            if isinstance(psycopg_err, psycopg_errors.Error):
                raise exceptions.ConnectorException from psycopg_err
            raise exceptions.ConnectorException from exc

    # Attaching a custom attribute to ease testability and make the
    # decorator more introspectable
    wrapped._exceptions_wrapped = True  # type: ignore
    return wrapped


class DjangoConnector(connector.BaseConnector):
    def __init__(
        self,
        *,
        json_dumps: Optional[Callable] = None,
        json_loads: Optional[Callable] = None,
        **kwargs: Any,
    ):
        self.json_dumps = json_dumps
        self.json_loads: Callable = json_loads or json.loads
        self._channels: Set[str] = set()

    def open(self, pool=None) -> None:
        pass

    def close(self) -> None:
        pass

    @wrap_exceptions
    def execute_query(self, query: str, **arguments: Any) -> None:
        query = self._prepare_for_interpolation(
            query=query, has_arguments=bool(arguments)
        )
        with django_connection.cursor() as cursor:
            cursor.execute(query, self._wrap_json(arguments))

    @wrap_exceptions
    def execute_query_one(self, query: str, **arguments: Any) -> Dict[str, Any]:
        query = self._prepare_for_interpolation(
            query=query, has_arguments=bool(arguments)
        )
        with django_connection.cursor() as cursor:
            cursor.execute(query, self._wrap_json(arguments))
            return self._dict_fetchone(cursor)

    @wrap_exceptions
    def execute_query_all(self, query: str, **arguments: Any) -> List[Dict[str, Any]]:
        query = self._prepare_for_interpolation(
            query=query, has_arguments=bool(arguments)
        )
        with django_connection.cursor() as cursor:
            cursor.execute(query, self._wrap_json(arguments))
            return self._dict_fetchall(cursor)

    def wait_for_notification(
        self, channels: Iterable[str], timeout: Optional[float] = None
    ) -> None:
        self._listen(channels)

        pg_conn = self._get_pg_conn(django_connection)
        if pg_conn.closed:
            return

        select.select([pg_conn], [], [], timeout)
        if not pg_conn.closed:
            pg_conn.poll()

        self._clear_read_notifies(pg_conn)

    def _wrap_json(self, arguments: Dict[str, Any]):
        return {
            key: Json(value, dumps=self.json_dumps)
            if isinstance(value, dict)
            else value
            for key, value in arguments.items()
        }

    def _load_row(self, cursor, row) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for val, col_desc in zip(row, cursor.description):
            if val is None:
                result[col_desc.name] = val
            elif col_desc.type_code == JSONB_OID:
                result[col_desc.name] = self.json_loads(val)
            else:
                result[col_desc.name] = val
        return result

    def _dict_fetchone(self, cursor) -> Dict[str, Any]:
        """Return row from a cursor as a dict"""
        return self._load_row(cursor, cursor.fetchone())

    def _dict_fetchall(self, cursor) -> List[Dict[str, Any]]:
        """Return all rows from a cursor as a dict"""
        return [self._load_row(cursor, row) for row in cursor.fetchall()]

    def _prepare_for_interpolation(self, query, has_arguments):
        # psycopg2 thinks ``%`` are for it to process. If we have ``%`` in our query,
        # like in RAISE, we need it to be passed to the database as-is, which means
        # we need to escape the % by doubling it.
        return (
            query
            if has_arguments or not isinstance(query, str)
            else query.replace("%", "%%")
        )

    def _make_dynamic_query(self, query: str, **identifiers: str) -> str:
        return psycopg2.sql.SQL(query).format(
            **{
                key: psycopg2.sql.Identifier(value)
                for key, value in identifiers.items()
            }
        )

    def _listen(self, channels: Iterable[str]) -> None:
        new_channels = set(channels) - self._channels
        for channel_name in new_channels:
            self.execute_query(
                query=self._make_dynamic_query(
                    query=sql.queries["listen_queue"], channel_name=channel_name
                ),
                channel_name=channel_name,
            )
            self._channels.add(channel_name)

    def _get_pg_conn(self, connection: ConnectionProxy) -> postgres_conn:
        connection.ensure_connection()
        return connection.connection

    def _clear_read_notifies(self, pg_conn: postgres_conn) -> None:
        pg_conn.notifies = [
            i for i in pg_conn.notifies if i.channel not in self._channels
        ]
