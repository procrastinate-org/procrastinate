# Use Procrastinate in a Django application

Many Django projects are deployed using PostgreSQL, so using procrastinate in
conjunction with Django would remove the necessity of having another broker to
schedule tasks, thereby reducing infrastructure costs.

## Configuration

To start, install procrastinate with:

```console
$ (venv) pip install 'procrastinate[django]'
```

Add procrastinate Django app to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...
    "procrastinate.contrib.django",
    ...
]
```
Optionally, you can set the following to ensure that the model instances exposed by
the Django integration are not modified through the ORM. Even if you don't,
most ORM modifications operations will be prevented.

```python
DATABASE_ROUTERS = ["procrastinate.contrib.django.ProcrastinateReadOnlyRouter", ...]
```

## Configuring the app

An app will be configured for you in `procrastinate.contrib.django.app`.
You don't have to configure an app yourself, but you can if you want to.

You can modify the app after its creation, for example to load additional tasks from
blueprints, with:

```python
# settings.py
PROCRASTINATE_ON_APP_READY = "myapp.procrastinate.on_app_ready"
```
```python
# myapp/procrastinate.py
import procrastinate

def on_app_ready(app: procrastinate.App):
    app.load_tasks_from(some_blueprint)
```


:::{note}
It's likely that configuring an app yourself and using it instead of the
one provided by Procrastinate will lead to all sorts of issues.
There's no hard requirement not to do it, but it might get complicated.
:::

## Defining tasks

After that, add your tasks to `tasks.py` in your Django app.
You can use the sync ORM API or the [async ORM API] to access your models.

```python
from procrastinate.contrib.django import app

@app.task
def mytask1(obj_pk):
    obj = MyModel.objects.get(pj=obj_pk)
    ...

@app.task
async def mytask2(obj_pk):
    obj = await MyModel.objects.aget(pj=obj_pk)
    ...
```

## Running the worker

Run the worker with the following command.
```console
$ (venv) ./manage.py procrastinate worker
```

`./manage.py procrastinate` mostly behaves like the `procrastinate` command
itself, with some commands removed and the app is configured for you.
You can also use other subcommands such as `./manage.py procrastinate defer`.

:::{note}
Procrastinate generates an app for you using a Psycopg or Aiopg connector
depending on your Django setup, and connects using the `DATABASES` settings.
:::

## Deferring jobs

Defer jobs from your views:
```python
from myapp.tasks import mytask

def myview(request):
    ...
    mytask.defer(obj_pk=obj.pk)

async def myasyncview(request):
    ...
    await mytask.defer_async(obj_pk=obj.pk)
```

## Migrations

Procrastinate comes with its own migrations so don't forget to run
`./manage.py migrate`. Procrastinate's Django migrations are always kept
in sync with your current version of Procrastinate, it's always a good idea
to check the release notes and read the migrations when upgrading.

## Models

Procrastinate exposes 2 of its internal tables as Django models. You can use
them to query the state of your jobs. They're also exposed in the Django admin.

:::{note}
We'll do our best to ensure backwards compatibility, but we won't always be
able to do so. If you use the models directly, make sure you test your
integration when upgrading Procrastinate.
:::

```python
from procrastinate.contrib.django.models import (
    ProcrastinateJob,
    ProcrastinateEvent,
)

ProcrastinateJob.objects.filter(task_name="mytask").count()
```

:::{note}
The models are read-only, you can't create, update or delete jobs or events
through the ORM.
:::

:::{note}
The `procrastinate_periodic_defers` table is not exposed as a Django model,
because it's mainly an internal table and we couldn't find a good use case
for it. If you find one, please [open an issue]!
:::

## Additional settings

If need be, Procrastinate exposes a few Django settings:

```python
# By default, the `tasks` module in each app is auto-discovered for tasks.
# You can change the name `tasks`` to something else, and add additional paths.

# Change the name of the module where tasks are auto-discovered.
# If set to None, auto-discovery is disabled except for paths in IMPORT_PATHS.
AUTODISCOVER_MODULE_NAME: str | None  # (defaults to "tasks")
# Dotted paths to additional modules containing tasks.
IMPORT_PATHS: list[str]  # (defaults  to [])

# If you just want to change the database alias used by the connector,
# you can use this setting (it has no effect if CREATE_CONNECTOR is set)
DATABASE_ALIAS: str,  # (defaults to "default")

# These settings are passed as-is to the App constructor.
WORKER_DEFAULTS: dict | None,  # (defaults to None)
PERIODIC_DEFAULTS: dict | None,  # (defaults to None)
```

## Logs

Procrastinate logs to the `procrastinate` logger. You can configure it
in your `LOGGING` settings.

## Advanced: Running the worker without the official management command
If you want to run the worker yourself, it's possible but slightly more convoluted.
Here's how you could do it:
```python
# myapp/worker.py
from procrastinate.contrib.django import app

def main():
    # By default, the app uses the Django database connection, which is unsuitable
    # for the worker.
    app = app.with_connector(app.connector.get_worker_connector())
    app.run_worker()

if __name__ == "__main__":
    main()
```
:::{note}
The ``.get_worker_connector()`` method is only available on `DjangoConnector`
and the API isn't guaranteed to be stable.

## Alternatives

It's worth noting that there are other Python job scheduling libraries based on
postgres' LISTEN/NOTIFY that integrate with Django. For instance,
[django-pgpubsub] is more focused on Django.

[django-pgpubsub]: https://readthedocs.org/projects/django-pgpubsub/
[async orm api]: https://docs.djangoproject.com/en/4.2/topics/async/#queries-the-orm
[contribute]: https://github.com/procrastinate-org/procrastinate/blob/main/CONTRIBUTING.md
[pending issues]: https://github.com/procrastinate-org/procrastinate/issues?q=is%3Aissue+is%3Aopen+django
[open an issue]: https://github.com/procrastinate-org/procrastinate/issues
[this talk at djangocon 2019]: https://www.youtube.com/watch?v=_DIlE-yc9ZQ
