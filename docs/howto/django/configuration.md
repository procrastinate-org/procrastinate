# Configure Django & Procrastinate to work together

Many Django projects are deployed using PostgreSQL, so using procrastinate in
conjunction with Django would remove the necessity of having another broker to
schedule tasks. Procrastinate is designed to play nicely with Django, let's see
how.

## Prerequisites

For each Python version supported by Procrastinate, Procastinate is tested with
the latest Django version supported by that Python version.

As of January 2025, this means Procrastinate is tested with Django 4.2 for
Python 3.8 and 3.9, and Django 5.1 for Python 3.10+. This paragraph is likely
to be outdated in the future, the best way to get up-to-date info is to have a
look at the `django` dependency group section of the [package
configuration](https://github.com/procrastinate-org/procrastinate/blob/main/pyproject.toml#L78-81)

## Installation & configuration

To start, install procrastinate with:

```console
(venv) $ pip install 'procrastinate[django]'
```

Add procrastinate Django app to your `INSTALLED_APPS`. You may want to add it
before your own apps to ensure that procrastinate is ready before your own code
runs.

```python
INSTALLED_APPS = [
    ...
    "procrastinate.contrib.django",
    ...
]
```

## Configuring the app

A Procrastinate app will be configured for you in
`procrastinate.contrib.django.app`. You don't have to configure an app
yourself.

You can modify the app after its creation, for example to load additional tasks
from blueprints, with:

```python
# settings.py
PROCRASTINATE_ON_APP_READY = "myapp.procrastinate.on_app_ready"
```

```python
# myapp/procrastinate.py
import procrastinate

def on_app_ready(app: procrastinate.App):
    app.add_tasks_from(some_blueprint)
```

:::{note}
While not recommended, you may decide to use a different app from the one
provided in `procrastinate.contrib.django.app`, it's not strictly incompatible,
but it might be more complicated and you may run into issues.
:::
