from __future__ import annotations

from typing import Any, NoReturn

from django.db import models

from . import exceptions, settings


def _read_only(*args, **kwargs) -> NoReturn:
    raise exceptions.ReadOnlyModel(
        "Procrastinate models exposed in Django, such as ProcrastinateJob "
        "are read-only. Please use the procrastinate CLI to interact with "
        "jobs."
    )


def _is_readonly() -> bool:
    return settings.settings.READONLY_MODELS


class ProcrastinateReadOnlyModelMixin:
    def save(self, *args, **kwargs) -> Any:
        if _is_readonly():
            _read_only()
        return super().save(*args, **kwargs)  # type: ignore

    def delete(self, *args, **kwargs) -> Any:
        if _is_readonly():
            _read_only()
        return super().delete(*args, **kwargs)  # type: ignore


_edit_methods = frozenset(
    (
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
    )
)


class ProcrastinateReadOnlyManager(models.Manager):
    def __getattribute__(self, name: str) -> Any:
        if name in _edit_methods and _is_readonly():
            return _read_only
        return super().__getattribute__(name)


class ProcrastinateJob(ProcrastinateReadOnlyModelMixin, models.Model):
    STATUSES = (
        "todo",
        "doing",
        "succeeded",
        "failed",
    )
    id = models.BigAutoField(primary_key=True)
    queue_name = models.CharField(max_length=128)
    task_name = models.CharField(max_length=128)
    priority = models.IntegerField()
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
    id = models.BigAutoField(primary_key=True)
    job = models.ForeignKey(ProcrastinateJob, on_delete=models.CASCADE)
    type = models.CharField(max_length=32, choices=[(e, e) for e in TYPES])
    at = models.DateTimeField(blank=True, null=True)

    objects = ProcrastinateReadOnlyManager()

    class Meta:  # type: ignore
        managed = False
        db_table = "procrastinate_events"


class ProcrastinatePeriodicDefer(ProcrastinateReadOnlyModelMixin, models.Model):
    id = models.BigAutoField(primary_key=True)
    task_name = models.CharField(max_length=128)
    defer_timestamp = models.BigIntegerField(blank=True, null=True)
    job = models.ForeignKey(
        ProcrastinateJob, on_delete=models.CASCADE, blank=True, null=True
    )
    periodic_id = models.CharField(max_length=128)

    class Meta:  # type: ignore
        managed = False
        db_table = "procrastinate_periodic_defers"
        unique_together = [("task_name", "periodic_id", "defer_timestamp")]
