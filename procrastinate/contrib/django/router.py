from __future__ import annotations

from . import exceptions


class ProcrastinateReadOnlyRouter:
    """
    This router prevents any write operation on the Procrastinate models.
    """

    def db_for_write(self, model, **hints):
        if model._meta.app_label == "procrastinate":
            raise exceptions.ReadOnlyModel(
                f"Procrastinate models exposed in Django, such as {model} are read-only. "
                "Please use the procrastinate CLI to interact with jobs."
            )
