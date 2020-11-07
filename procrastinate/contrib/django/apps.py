from django.apps import AppConfig

from procrastinate.contrib.django import migrations_magic


class ProcrastinateConfig(AppConfig):
    name = "procrastinate.contrib.django"
    label = "procrastinate"

    def ready(self) -> None:
        migrations_magic.load()
