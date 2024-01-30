from __future__ import annotations

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
