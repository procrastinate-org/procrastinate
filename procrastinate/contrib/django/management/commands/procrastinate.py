from __future__ import annotations

import asyncio
import contextlib
import os

from django.core.management.base import BaseCommand

from procrastinate import cli
from procrastinate.contrib.django import app, django_connector, healthchecks


class Command(BaseCommand):
    help = "Access procrastinate commands"

    def add_arguments(self, parser):
        self._django_options = {a.dest for a in parser._actions}
        cli.add_arguments(
            parser,
            include_app=False,
            include_schema=False,
            custom_healthchecks=healthchecks.healthchecks,
        )

    suppressed_base_arguments = {"-v", "--version"}

    def handle(self, *args, **kwargs):
        if os.name == "nt":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

        kwargs = {k: v for k, v in kwargs.items() if k not in self._django_options}
        context = contextlib.nullcontext()

        if isinstance(app.connector, django_connector.DjangoConnector):
            kwargs["app"] = app
            context = app.replace_connector(app.connector.get_worker_connector())

        with context:
            asyncio.run(cli.execute_command(kwargs))
