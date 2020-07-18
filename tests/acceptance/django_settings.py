import os

SECRET_KEY = "test"
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.environ.get("PGDATABASE_DJANGO", "procrastinate"),
        "USER": os.environ.get("PGUSER", "postgres"),
        "PASSWORD": os.environ.get("PGPASSWORD", "password"),
        "HOST": os.environ.get("PGHOST", "localhost"),
    },
}

INSTALLED_APPS = [
    "procrastinate.contrib.django",
]
