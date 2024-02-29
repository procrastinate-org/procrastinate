from __future__ import annotations

from typing import cast

from procrastinate import app as app_module

from .placeholder import FutureApp
from .router import ProcrastinateReadOnlyRouter
from .utils import connector_params

__all__ = [
    "app",
    "connector_params",
    "ProcrastinateReadOnlyRouter",
]
default_app_config = "procrastinate.contrib.django.apps.ProcrastinateConfig"

# Before the Django app is ready, we're defining the app as a blueprint so
# that tasks can be registered. The real app will be initialized in the
# ProcrastinateConfig.ready() method.
# This blueprint has special implementations for App method so that if
# users try to use the app before it's ready, they get a helpful error message.
app: app_module.App = cast(app_module.App, FutureApp())
