from __future__ import annotations

from typing import Iterable

from django import apps
from django.utils import module_loading

import procrastinate
from procrastinate.contrib import django as contrib_django
from procrastinate.contrib.django import migrations_magic, utils

from . import django_connector


class ProcrastinateConfig(apps.AppConfig):
    name = "procrastinate.contrib.django"
    label = "procrastinate"

    def ready(self) -> None:
        migrations_magic.load()
        contrib_django.app = create_app(blueprint=contrib_django.app)

    @property
    def app(self) -> procrastinate.App:
        return contrib_django.app


def get_import_paths() -> Iterable[str]:
    module_name = utils.get_setting("AUTODISCOVER_MODULE_NAME", default="tasks")
    if module_name:
        # It's ok that we don't yield the discovered modules here, the
        # important thing is that they are imported.
        module_loading.autodiscover_modules(module_name)

    yield from utils.get_setting("IMPORT_PATHS", default=[])


def create_app(blueprint: procrastinate.Blueprint) -> procrastinate.App:
    connector = django_connector.DjangoConnector(
        alias=utils.get_setting("DATABASE_ALIAS", default="default")
    )
    app = procrastinate.App(
        connector=connector,
        import_paths=list(get_import_paths()),
        worker_defaults=utils.get_setting("WORKER_DEFAULTS", default=None),
        periodic_defaults=utils.get_setting("PERIODIC_DEFAULTS", default=None),
    )

    if blueprint.tasks:
        app.add_tasks_from(blueprint, namespace="")

    return app
