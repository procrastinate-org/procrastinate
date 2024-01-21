from __future__ import annotations

from typing import cast

import procrastinate

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
app: procrastinate.App = cast(procrastinate.App, procrastinate.Blueprint())
