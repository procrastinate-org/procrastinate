from __future__ import annotations

from .procrastinate_app import app
from .utils import connector_params

__all__ = [
    "app",
    "connector_params",
]
default_app_config = "procrastinate.contrib.django.apps.ProcrastinateConfig"
