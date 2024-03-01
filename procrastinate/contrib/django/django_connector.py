from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any, Iterable

import asgiref.sync
from django.core import exceptions as django_exceptions
from django.db import connections
from django.db.backends.base.base import BaseDatabaseWrapper
from typing_extensions import LiteralString

from procrastinate import connector
from procrastinate.contrib.django import utils

if TYPE_CHECKING:
    from psycopg.types.json import Jsonb
else:
    try:
        from django.db.backends.postgresql.psycopg_any import Jsonb
    except ImportError:
        from psycopg2.extras import Json as Jsonb


class DjangoConnector(connector.BaseAsyncConnector):
    """
    The Django connector doesn't use a pool, but instead uses the Django
    connection. It is meant to be used in Django applications, and is
    automatically configured when using the Django app.
    """

    def __init__(self, alias: str = "default") -> None:
        self.alias = alias

    def get_sync_connector(self) -> connector.BaseConnector:
        return self

    @property
    def connection(self) -> BaseDatabaseWrapper:
        return connections[self.alias]  # type: ignore

    def open(self, pool: None = None) -> None:
        if pool:
            raise django_exceptions.ImproperlyConfigured(
                "Pool is not supported in Django connectors"
            )
        pass

    async def open_async(self, pool: None = None) -> None:
        if pool:
            raise django_exceptions.ImproperlyConfigured(
                "Pool is not supported in Django connectors"
            )
        pass

    def close(self) -> None:
        pass

    async def close_async(self) -> None:
        pass

    async def execute_query_async(self, query: LiteralString, **arguments: Any) -> None:
        return await asgiref.sync.sync_to_async(self.execute_query)(
            query=query, **arguments
        )

    async def execute_query_one_async(
        self, query: LiteralString, **arguments: Any
    ) -> dict[str, Any]:
        return await asgiref.sync.sync_to_async(self.execute_query_one)(
            query=query, **arguments
        )

    async def execute_query_all_async(
        self, query: LiteralString, **arguments: Any
    ) -> list[dict[str, Any]]:
        return await asgiref.sync.sync_to_async(self.execute_query_all)(
            query=query, **arguments
        )

    def _dictfetch(self, cursor):
        "Return all rows from a cursor as a dict"
        columns = [col[0] for col in cursor.description]
        return (dict(zip(columns, row)) for row in cursor.fetchall())

    def _wrap_json(self, arguments: dict[str, Any]) -> dict[str, Any]:
        return {
            key: Jsonb(value) if isinstance(value, dict) else value
            for key, value in arguments.items()
        }

    def execute_query(self, query: LiteralString, **arguments: Any) -> None:
        with self.connection.cursor() as cursor:
            cursor.execute(query, self._wrap_json(arguments))

    def execute_query_one(
        self, query: LiteralString, **arguments: Any
    ) -> dict[str, Any]:
        with self.connection.cursor() as cursor:
            cursor.execute(query, self._wrap_json(arguments))
            return next(self._dictfetch(cursor))

    def execute_query_all(
        self, query: LiteralString, **arguments: Any
    ) -> list[dict[str, Any]]:
        with self.connection.cursor() as cursor:
            cursor.execute(query, self._wrap_json(arguments))
            return list(self._dictfetch(cursor))

    async def listen_notify(
        self, event: asyncio.Event, channels: Iterable[str]
    ) -> None:
        raise NotImplementedError(
            "listen/notify is not supported with Django connector"
        )

    def get_worker_connector(self) -> connector.BaseAsyncConnector:
        """
        The default DjangoConnector is not suitable for workers. This function
        returns a connector that uses the same database and is suitable for workers.
        The type of connector returned is a `PsycopgConnector` if psycopg3 is installed,
        otherwise an `AiopgConnector`.

        Returns
        -------
        ``procrastinate.contrib.aiopg.AiopgConnector`` or ``procrastinate.contrib.psycopg3.PsycopgConnector``
            A connector that can be used in a worker
        """
        alias = utils.get_setting("DATABASE_ALIAS", default="default")

        if utils.package_is_installed("psycopg") and utils.package_is_version(
            "psycopg", 3
        ):
            from procrastinate import psycopg_connector

            return psycopg_connector.PsycopgConnector(
                kwargs=utils.connector_params(alias)
            )
        if utils.package_is_installed("aiopg"):
            from procrastinate.contrib.aiopg import aiopg_connector

            return aiopg_connector.AiopgConnector(**utils.connector_params(alias))

        raise django_exceptions.ImproperlyConfigured(
            "You must install either psycopg(3) or aiopg to use "
            "``./manage.py procrastinate`` or "
            "``app.connector.get_worker_connector()``."
        )
