from __future__ import annotations

from django.utils.crypto import get_random_string

SECRET_KEY = get_random_string(50)

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    "procrastinate_demos.demo_django.demo",
    "procrastinate.contrib.django",
]


MIDDLEWARE = [
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
]

ROOT_URLCONF = "procrastinate_demos.demo_django.project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
            ],
        },
    },
]

WSGI_APPLICATION = "procrastinate_demos.demo_django.project.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "procrastinate",
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGGING = {
    "version": 1,
    "formatters": {
        "procrastinate": {"format": "%(asctime)s %(levelname)-7s %(name)s %(message)s"},
    },
    "handlers": {
        "procrastinate": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "procrastinate",
        },
    },
    "loggers": {
        "procrastinate": {
            "handlers": ["procrastinate"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}
