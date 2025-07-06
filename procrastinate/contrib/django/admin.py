from __future__ import annotations

import json

from django.contrib import admin
from django.db.models import Prefetch
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.urls import path, reverse
from django.utils import timezone
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe

from procrastinate.utils import ellipsize_middle

from . import models

JOB_STATUS_EMOJI_MAPPING = {
    "todo": "🗓️",
    "doing": "🚂",
    "failed": "❌",
    "succeeded": "✅",
    "cancelled": "🤚",
    "aborting": "🔌🕑️",  # legacy, not used anymore
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
    ]
    list_display = [
        "pk",
        "short_task_name",
        "pretty_args",
        "pretty_status",
        "summary",
    ]
    list_filter = [
        "status",
        "queue_name",
        "task_name",
        "lock",
        "queueing_lock",
        "scheduled_at",
        "priority",
    ]
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

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .prefetch_related(
                Prefetch(
                    "procrastinateevent_set",
                    queryset=models.ProcrastinateEvent.objects.order_by("-at"),
                )
            )
        )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<int:job_id>/full_args/",
                self.admin_site.admin_view(self.full_args_view),
                name="full_args",
            ),
        ]
        return custom_urls + urls

    @admin.display(description="Status")
    def pretty_status(self, instance: models.ProcrastinateJob) -> str:
        emoji = JOB_STATUS_EMOJI_MAPPING.get(instance.status, "")
        return f"{emoji} {instance.status.title()}"

    @admin.display(description="Task Name")
    def short_task_name(self, instance: models.ProcrastinateJob) -> str:
        *modules, name = instance.task_name.split(".")
        return format_html(
            "<span title='{task_name}'>{name}</span>",
            task_name=instance.task_name,
            name=".".join(m[0] for m in modules) + f".{name}",
        )

    @admin.display(description="Args")
    def pretty_args(self, instance: models.ProcrastinateJob) -> str:
        rows = format_html_join(
            "\n",
            "<tr><td>{}</td><td>{}</td></tr>",
            (
                (key, ellipsize_middle(json.dumps(value)))
                for key, value in instance.args.items()
            ),
        )
        return format_html(
            "<table>{rows}</table>"
            '<div style="margin-top: 8px"><a href="{full_args_url}">View unformatted</a></div>',
            rows=rows,
            full_args_url=reverse("admin:full_args", kwargs={"job_id": instance.id}),
        )

    @admin.display(description="Summary")
    def summary(self, instance: models.ProcrastinateJob) -> str:
        if last_event := instance.procrastinateevent_set.first():  # type: ignore[attr-defined]
            return mark_safe(
                render_to_string(
                    "procrastinate/admin/summary.html",
                    {
                        "last_event": last_event,
                        "job": instance,
                        "now": timezone.now(),
                    },
                ).strip()
            )
        return ""

    def full_args_view(self, request, job_id):
        instance = models.ProcrastinateJob.objects.get(id=job_id)
        return JsonResponse(instance.args)
