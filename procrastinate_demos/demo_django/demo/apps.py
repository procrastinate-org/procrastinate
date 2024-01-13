from django.apps import AppConfig

from .. import procrastinate_app


class DemoConfig(AppConfig):
    name = "procrastinate_demos.demo_django.demo"

    def ready(self) -> None:
        procrastinate_app.app.open()
