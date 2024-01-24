from __future__ import annotations

from django.contrib import admin

from . import models


class ProcrastinateAdmin(admin.ModelAdmin):
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


admin.site.register(
    [
        models.ProcrastinateJob,
        models.ProcrastinateEvent,
    ],
    ProcrastinateAdmin,
)
