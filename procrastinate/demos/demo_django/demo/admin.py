from __future__ import annotations

from django.contrib import admin

from . import models

admin.site.register(models.Book)
