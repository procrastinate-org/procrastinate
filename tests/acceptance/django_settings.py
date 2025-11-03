from __future__ import annotations

import os

SECRET_KEY = "test"
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("PGDATABASE", "procrastinate"),
        "TEST": {"NAME": "procrastinate_django_test"},
        "OPTIONS": {"pool": {"min_size": 1, "max_size": 4}},
    },
}
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "procrastinate.contrib.django",
]
USE_TZ = True  # To avoid RemovedInDjango50Warning
