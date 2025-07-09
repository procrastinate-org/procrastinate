from __future__ import annotations

import json
import logging

from django.contrib import admin, messages
from django.db import transaction
from django.db.models import Prefetch
from django.db.models.functions import Now
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from . import models

logger = logging.getLogger(__name__)

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


@admin.action(
    description="Reschedule marked jobs to run now", permissions=["reschedule"]
)
def reschedule(modeladmin, request, queryset):
    """
    Reschedule marked jobs to run now.
    Only processes jobs that are scheduled for the future and in 'todo' status.
    """
    # Use transaction to ensure atomic updates
    with transaction.atomic():
        # Filter to only jobs that are scheduled for the future and in 'todo' status
        eligible_jobs = queryset.select_for_update().filter(
            status="todo", scheduled_at__gt=Now()
        )

        # Count jobs for user feedback
        total_selected = queryset.count()
        eligible_count = eligible_jobs.count()
        skipped_count = total_selected - eligible_count

        try:
            # Update the scheduled_at time to now for eligible jobs
            updated_count = eligible_jobs.update(scheduled_at=Now())

            if updated_count > 0:
                messages.success(
                    request,
                    f"Successfully moved {updated_count} job{'s' if updated_count != 1 else ''} to run immediately.",
                )

            if skipped_count > 0:
                messages.info(
                    request,
                    f"Skipped {skipped_count} job{'s' if skipped_count != 1 else ''} "
                    "(not scheduled for future or not in 'todo' status).",
                )

        except Exception as e:
            logger.exception("Failed to reschedule jobs")
            messages.error(
                request,
                f"Failed to reschedule jobs: {e}",
            )


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
    actions = [reschedule]

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

    def has_reschedule_permission(self, request, obj=None):
        """
        Check if the user has change permission on ProcrastinateJob.
        """
        return super().has_change_permission(request)

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
        indent = 2 if len(instance.args) > 1 or len(str(instance.args)) > 30 else None
        pretty_json = json.dumps(instance.args, indent=indent)
        if len(pretty_json) > 2000:
            pretty_json = pretty_json[:2000] + "..."
        return format_html(
            '<pre style="margin: 0">{pretty_json}</pre>', pretty_json=pretty_json
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
