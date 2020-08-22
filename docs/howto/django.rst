Use Procrastinate in a Django application
=========================================

Add Procrastinate in your ``INSTALLED_APPS``::

    INSTALLED_APPS = [
        ...
        "procrastinate.contrib.django",
    ]

Procrastinate comes with its own migrations so don't forget to call ``./manage.py
migrate``.

As of now, Procrastinate cannot read Postgresql connection settings from Django
settings, so you'll need to configure it manually (see `connector`).

