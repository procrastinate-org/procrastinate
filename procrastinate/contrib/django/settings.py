from __future__ import annotations

from typing import Any, ClassVar

from django.conf import settings as django_settings
from typing_extensions import dataclass_transform


@dataclass_transform()
class BaseSettings:
    def __getattribute__(self, name: str) -> Any:
        return getattr(
            django_settings,
            f"PROCRASTINATE_{name}",
            getattr(type(self), name),
        )


class Settings(BaseSettings):
    AUTODISCOVER_MODULE_NAME: ClassVar[str] = "tasks"
    IMPORT_PATHS: ClassVar[list[str]] = []
    DATABASE_ALIAS: ClassVar[str] = "default"
    WORKER_DEFAULTS: ClassVar[dict[str, str] | None] = None
    PERIODIC_DEFAULTS: ClassVar[dict[str, str] | None] = None
    ON_APP_READY: ClassVar[str | None] = None
    READONLY_MODELS: ClassVar[bool] = True


settings = Settings()
