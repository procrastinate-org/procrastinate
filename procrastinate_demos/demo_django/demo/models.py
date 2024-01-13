from __future__ import annotations

from django.db import models


class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    indexed = models.BooleanField(default=False)

    class Meta:  # pyright: ignore [reportIncompatibleVariableOverride]
        app_label = "demo"
