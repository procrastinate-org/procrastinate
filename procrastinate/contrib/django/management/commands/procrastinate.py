from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from django.core.management.base import BaseCommand

from procrastinate import cli, psycopg_connector
from procrastinate.contrib.aiopg import aiopg_connector
from procrastinate.contrib.django import app, apps, utils

if TYPE_CHECKING:
    is_psycopg3 = True
else:
    try:
        from django.db.backends.postgresql.psycopg_any import is_psycopg3
    except ImportError:
        is_psycopg3 = False


class Command(BaseCommand):
    help = "Access procrastinate commands"

    def add_arguments(self, parser):
        self._django_options = {a.dest for a in parser._actions}
        cli.add_arguments(
            parser,
            include_app=False,
            include_schema=False,
            include_healthchecks=False,
        )

    def handle(self, *args, **kwargs):
        kwargs = {k: v for k, v in kwargs.items() if k not in self._django_options}
        kwargs["app"] = app.with_connector(self.get_connector())
        asyncio.run(cli.execute_command(kwargs))

    def get_connector(self):
        # It's not possible to use the Django connector for the worker, so
        # it's easier to just a classic Procrastinate connector.
        alias = apps.get_setting("DATABASE_ALIAS", default="default")

        if is_psycopg3:
            return psycopg_connector.PsycopgConnector(
                kwargs=utils.connector_params(alias)
            )
        else:
            return aiopg_connector.AiopgConnector(**utils.connector_params(alias))
