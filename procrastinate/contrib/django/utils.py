from __future__ import annotations

from typing import Any

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
    return wrapper.get_connection_params()
