import os

SECRET_KEY = "test"
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.environ.get("PGDATABASE", "procrastinate"),
    },
}

INSTALLED_APPS = [
    "procrastinate.contrib.django",
]
