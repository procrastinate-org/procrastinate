from django.db import models


class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    indexed = models.BooleanField(default=False)

    class Meta:
        app_label = "demo"
