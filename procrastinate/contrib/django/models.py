from __future__ import annotations

from typing import Any, NoReturn

from django.db import models

from . import exceptions


def _read_only(*args, **kwargs) -> NoReturn:
    raise exceptions.ReadOnlyModel(
        "Procrastinate models exposed in Django, such as ProcrastinateJob "
        "are read-only. Please use the procrastinate CLI to interact with "
        "jobs."
    )


class ProcrastinateReadOnlyModelMixin:
    def save(self, *args, **kwargs) -> NoReturn:
        _read_only()

    def delete(self, *args, **kwargs) -> NoReturn:
        _read_only()


class ProcrastinateReadOnlyManager(models.Manager):
    def __getattribute__(self, __name: str) -> Any:
        if __name in [
            "create",
            "acreate",
            "get_or_create",
            "aget_or_create",
            "bulk_create",
            "abulk_create",
            "update",
            "aupdate",
            "update_or_create",
            "aupdate_or_create",
            "bulk_update",
            "abulk_update",
            "delete",
            "adelete",
        ]:
            return _read_only
        return super().__getattribute__(__name)


class ProcrastinateJob(ProcrastinateReadOnlyModelMixin, models.Model):
    STATUSES = (
        "todo",
        "doing",
        "succeeded",
        "failed",
    )
    queue_name = models.CharField(max_length=128)
    task_name = models.CharField(max_length=128)
    lock = models.TextField(unique=True, blank=True, null=True)
    args = models.JSONField()
    status = models.CharField(max_length=32, choices=[(e, e) for e in STATUSES])
    scheduled_at = models.DateTimeField(blank=True, null=True)
    attempts = models.IntegerField()
    queueing_lock = models.TextField(unique=True, blank=True, null=True)

    objects = ProcrastinateReadOnlyManager()

    class Meta:  # type: ignore
        managed = False
        db_table = "procrastinate_jobs"


class ProcrastinateEvent(ProcrastinateReadOnlyModelMixin, models.Model):
    TYPES = (
        "deferred",
        "started",
        "deferred_for_retry",
        "failed",
        "succeeded",
        "cancelled",
        "scheduled",
    )
    job = models.ForeignKey(ProcrastinateJob, on_delete=models.CASCADE)
    type = models.CharField(max_length=32, choices=[(e, e) for e in TYPES])
    at = models.DateTimeField(blank=True, null=True)

    objects = ProcrastinateReadOnlyManager()

    class Meta:  # type: ignore
        managed = False
        db_table = "procrastinate_events"
