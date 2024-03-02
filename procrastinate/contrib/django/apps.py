from __future__ import annotations

from typing import Iterable

from django import apps
from django.utils import module_loading

import procrastinate

from . import django_connector, migrations_magic, procrastinate_app, utils


class ProcrastinateConfig(apps.AppConfig):
    name = "procrastinate.contrib.django"
    label = "procrastinate"

    def ready(self) -> None:
        migrations_magic.load()
        procrastinate_app._current_app = create_app(
            blueprint=procrastinate_app._current_app
        )

    @property
    def app(self) -> procrastinate.App:
        return procrastinate_app.app


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

    on_app_ready_path = utils.get_setting("ON_APP_READY", default=None)
    if on_app_ready_path:
        on_app_ready = module_loading.import_string(on_app_ready_path)
        on_app_ready(app)

    return app
