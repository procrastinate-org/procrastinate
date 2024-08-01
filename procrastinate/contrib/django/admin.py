from __future__ import annotations

from django.contrib import admin
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from . import models

JOB_STATUS_EMOJI_MAPPING = {
    "todo": "🗓️",
    "doing": "🚂",
    "failed": "❌",
    "succeeded": "✅",
    "cancelled": "🤚",
    "aborting": "🔌🕑️",
    "aborted": "🔌",
}


class ProcrastinateEventInline(admin.StackedInline):
    model = models.ProcrastinateEvent


@admin.register(models.ProcrastinateJob)
class ProcrastinateJobAdmin(admin.ModelAdmin):
    fields = [
        "pk",
        "short_task_name",
        "pretty_args",
        "pretty_status",
        "queue_name",
        "lock",
        "queueing_lock",
        "priority",
        "scheduled_at",
        "attempts",
        "summary",
    ]
    list_display = [
        "pk",
        "short_task_name",
        "pretty_args",
        "pretty_status",
        "queue_name",
        "lock",
        "queueing_lock",
        "priority",
        "scheduled_at",
        "attempts",
    ]
    list_filter = ["status"]
    inlines = [ProcrastinateEventInline]

    def get_readonly_fields(
        self,
        request,
        obj=None,
    ):
        return [
            field.name
            for field in type(obj)._meta.get_fields()  # type: ignore
            if field.concrete
        ]

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.display(description="Status")
    def pretty_status(self, instance: models.ProcrastinateJob) -> str:
        emoji = JOB_STATUS_EMOJI_MAPPING.get(instance.status, "")
        return f"{emoji} ({instance.status})"

    @admin.display(description="Task Name")
    def short_task_name(self, instance: models.ProcrastinateJob) -> str:
        *modules, name = instance.task_name.split(".")
        return ".".join(m[0] for m in modules) + f".{name}"

    @admin.display(description="Args")
    def pretty_args(self, instance: models.ProcrastinateJob) -> str:
        return mark_safe(f"<pre>{instance.args}</pre>")

    @admin.display(description="Summary")
    def summary(self, instance: models.ProcrastinateJob) -> str:
        if last_event := instance.procrastinateevent_set.latest():  # type: ignore[attr-defined]
            return mark_safe(
                render_to_string("summary.html", {"last_event": last_event}).strip()
            )
        return ""
