from __future__ import annotations

import functools
import re
from typing import Any, Callable, Mapping

import psycopg2.errors
import sqlalchemy
from psycopg2.extras import Json

from procrastinate import connector, exceptions


def wrap_exceptions(func: Callable) -> Callable:
    """
    Wrap SQLAlchemy errors as connector exceptions.
    """

    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except sqlalchemy.exc.IntegrityError as exc:
            if isinstance(exc.orig, psycopg2.errors.UniqueViolation):
                raise exceptions.UniqueViolation(
                    constraint_name=exc.orig.diag.constraint_name
                )
            raise exceptions.ConnectorException from exc
        except sqlalchemy.exc.SQLAlchemyError as exc:
            raise exceptions.ConnectorException from exc

    # Attaching a custom attribute to ease testability and make the
    # decorator more introspectable
    wrapped._exceptions_wrapped = True  # type: ignore
    return wrapped


def wrap_query_exceptions(func: Callable) -> Callable:
    """
    Detect "admin shutdown" errors and retry once.

    This is to handle the case where the database connection (obtained from the pool)
    was actually closed by the server. In this case, SQLAlchemy raises a ``DBAPIError``
    with ``connection_invalidated`` set to ``True``, and also invalidates the rest of
    the connection pool. So we just retry once, to get a fresh connection.
    """

    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except sqlalchemy.exc.DBAPIError as exc:
            if exc.connection_invalidated:
                return func(*args, **kwargs)
            raise exc

    return wrapped


PERCENT_PATTERN = re.compile(r"%(?![\(s])")


class SQLAlchemyPsycopg2Connector(connector.BaseConnector):
    def __init__(
        self,
        *,
        dsn: str = "postgresql://",
        json_dumps: Callable | None = None,
        json_loads: Callable | None = None,
        **kwargs: Any,
    ):
        """
        Synchronous connector based on SQLAlchemy with Psycopg2.

        All other arguments than ``dsn``, ``json_dumps``, and ``json_loads`` are passed
        to :py:func:`create_engine` (see SQLAlchemy documentation__).

        .. __: https://docs.sqlalchemy.org/en/latest/core/engines.html#sqlalchemy.create_engine

        Parameters
        ----------
        dsn : The dsn string or URL object passed to SQLAlchemy's ``create_engine``
            function. Ignored if the engine is externally created and set into the
            connector through the ``App.open`` method.
        json_dumps :
            The JSON dumps function to use for serializing job arguments. Defaults to
            the function used by psycopg2. See the `psycopg2 doc`_.
        json_loads :
            The JSON loads function to use for deserializing job arguments. Defaults
            Python's ``json.loads`` function.
        """
        self.json_dumps = json_dumps
        self.json_loads = json_loads
        self._engine: sqlalchemy.engine.Engine | None = None
        self._engine_dsn = dsn
        self._engine_kwargs = kwargs
        self._engine_externally_set = False

    @wrap_exceptions
    def open(self, engine: sqlalchemy.engine.Engine | None = None) -> None:
        """
        Create an SQLAlchemy engine for the connector.

        Parameters
        ----------
        engine :
            Optional engine. Procrastinate can use an existing engine. If set the
            engine dsn and arguments passed in the constructor will be ignored.
        """
        if engine:
            self._engine_externally_set = True
            self._engine = engine
        else:
            self._engine = self._create_engine(self._engine_dsn, self._engine_kwargs)

    def get_sync_connector(self) -> connector.BaseConnector:
        return self

    @staticmethod
    def _create_engine(
        dsn: str, engine_kwargs: dict[str, Any]
    ) -> sqlalchemy.engine.Engine:
        """
        Create an SQLAlchemy engine.
        """
        return sqlalchemy.create_engine(url=dsn, **engine_kwargs)

    @wrap_exceptions
    def close(self) -> None:
        """
        Dispose of the connection pool used by the SQLAlchemy engine.
        """
        if not self._engine_externally_set and self._engine:
            self._engine.dispose()
        self._engine = None

    @property
    def engine(self) -> sqlalchemy.engine.Engine:
        if self._engine is None:  # Set by open
            raise exceptions.AppNotOpen
        return self._engine

    def _wrap_json(self, arguments: dict[str, Any]):
        return {
            key: Json(value, dumps=self.json_dumps)
            if isinstance(value, dict)
            else value
            for key, value in arguments.items()
        }

    @wrap_exceptions
    @wrap_query_exceptions
    def execute_query(self, query: str, **arguments: Any) -> None:
        with self.engine.begin() as connection:
            connection.exec_driver_sql(
                PERCENT_PATTERN.sub("%%", query), self._wrap_json(arguments)
            )

    @wrap_exceptions
    @wrap_query_exceptions
    def execute_query_one(self, query: str, **arguments: Any) -> Mapping[str, Any]:
        with self.engine.begin() as connection:
            cursor_result = connection.exec_driver_sql(
                PERCENT_PATTERN.sub("%%", query), self._wrap_json(arguments)
            )
            mapping = cursor_result.mappings()
            # psycopg2's type say it returns a tuple, but it actually returns a
            # dict when configured with RealDictCursor
            return mapping.fetchone()  # type: ignore

    @wrap_exceptions
    @wrap_query_exceptions
    def execute_query_all(
        self, query: str, **arguments: Any
    ) -> list[Mapping[str, Any]]:
        with self.engine.begin() as connection:
            cursor_result = connection.exec_driver_sql(
                PERCENT_PATTERN.sub("%%", query), self._wrap_json(arguments)
            )
            mapping = cursor_result.mappings()
            # psycopg2's type say it returns a tuple, but it actually returns a
            # dict when configured with RealDictCursor
            return mapping.all()  # type: ignore
