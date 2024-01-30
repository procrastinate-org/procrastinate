from __future__ import annotations

import asyncio

from django.core.management.base import BaseCommand

from procrastinate import cli
from procrastinate.contrib.django import app, django_connector


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
        if isinstance(app.connector, django_connector.DjangoConnector):
            kwargs["app"] = app.with_connector(app.connector.get_worker_connector())
        asyncio.run(cli.execute_command(kwargs))
