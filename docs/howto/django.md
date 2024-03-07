# Django integration

While we tries our best for Procrastinate to be easily integrated into diverse
kinds of applications, Django is special enough and widely used enough to have a
special integration.

Within Django, Procrastrinate will configure its app for you, using Django's
Database settings, and load tasks automatically from your apps. It will also
provide a few Django models & admin pages to look at the Procrastinate tables
from within Django. Django migrations are also provided so that you don't need
to handle multiple migration systems.

The following pages will guide you through the specifics of using Procrastinate
within a Django app.

:::{toctree}

django/configuration
django/basic_usage
django/migrations
django/models
django/settings
django/logs
django/tests
django/startup_actions
django/scripts
:::
