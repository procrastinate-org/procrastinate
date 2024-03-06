from __future__ import annotations

import os

SECRET_KEY = "test"
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.environ.get("PGDATABASE", "procrastinate"),
        "TEST": {"NAME": "procrastinate_django_test"},
    },
}
INSTALLED_APPS = [
    "procrastinate.contrib.django",
]
USE_TZ = True  # To avoid RemovedInDjango50Warning
