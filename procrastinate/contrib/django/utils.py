from __future__ import annotations

import importlib.util
import importlib.metadata
from typing import Any

from django.conf import settings
from django.db import connections


def connector_params(alias: str = "default") -> dict[str, Any]:
    """
    Returns parameters for in a format that is suitable to be passed to a
    connector constructor (see `howto/django`).

    Parameters
    ----------
    alias :
        Alias of the database, to read in the keys of settings.DATABASES,
        by default ``default``.

    Returns
    -------
    ``Dict[str, Any]``
        Provide these keyword arguments when instantiating your connector
    """
    wrapper = connections[alias]
    params = wrapper.get_connection_params()
    params.pop("cursor_factory", None)
    params.pop("context", None)
    return params


def get_setting(name: str, *, default) -> Any:
    return getattr(settings, f"PROCRASTINATE_{name}", default)


def package_is_installed(name: str) -> bool:
    return bool(importlib.util.find_spec(name))


def package_is_version(name: str, version: int) -> bool:
    """Assumes the version is written with dots"""
    v = metadata.version(name)
    if "." not in v:
        return False
    return int(v.split(".")[0]) == version
