# Use Procrastinate in a Django application

## Defining tasks

Add your tasks to `tasks.py` in your Django app.
Inside tasks, you can use the classical ORM API or the [async ORM API] to access your models.

[async ORM API]: https://docs.djangoproject.com/en/4.2/topics/async/#queries-the-orm

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

See {doc}`../basics/tasks` for more details on how to define tasks.

## Running the worker & other CLI commands

Run the worker with the following command.

```console
(venv) $ ./manage.py procrastinate worker
```

`./manage.py procrastinate` mostly behaves like the `procrastinate` command
itself. The subcommand `schema` is not available, as Procrastinate will use
Django migrations. The `--app` option is also not available, as Procrastinate will use
the automatically provided app (see {doc}`configuration`).

:::{note}
As a fully async connector is needed to run the worker, Procrastinate generates
one for you using `Psycopg` (by default) or `Aiopg` depending on
whether `psycopg` version 3 or `aiopg` is installed, and connects using the
`DATABASES` settings. If neither library is installed, an error will be raised.
:::

:::{note}
Contrary to the standalone `procrastinate` CLI, `./manage.py procrastinate`
does not support changing the verbosity with `-v`. `-v` is a django-controlled
argument and will not be used by Procrastinate. Define your logging configuration
in Django's settings (see {doc}`logs`).
:::

See {doc}`../basics/command_line` for more details on the CLI.
If you prefer writing your own scripts, see {doc}`scripts`.

## Database connections

The worker manages Django's database connections around each task the same way
Django does around an HTTP request: per-thread connections are closed before and
after every task (sync or async) via `close_old_connections()`, and Django's
query log (only populated under `DEBUG=True`) is cleared with `reset_queries()`.
You don't need to manage connections in your tasks, and `CONN_MAX_AGE` is
respected, so persistent connections are reused between tasks rather than
force-closed.

Because the connection is only closed at these task boundaries (not in between), a
connection opened early in a long-running task stays open until the task finishes,
even across a long stretch of non-database work. If that matters — to free a
connection slot, or to avoid reusing a connection that may have dropped while
idle — close it from within the task once you're done with the database for a
while:

```python
from django.db import close_old_connections

@app.task
def long_task():
    do_early_db_work()
    close_old_connections()  # release the connection before the long idle stretch
    do_hours_of_non_db_work()
    do_late_db_work()  # reconnects fresh
```

## Deferring jobs

Defer jobs from your views works as you would expect:

```python
from myapp.tasks import mytask

def myview(request):
    ...
    mytask.defer(obj_pk=obj.pk)

async def myasyncview(request):
    ...
    await mytask.defer_async(obj_pk=obj.pk)
```

See {doc}`../basics/defer` for more details on how to defer jobs.

## Checking proper configuration

You can check that Procrastinate is properly configured by running the following command:

```console
(venv) $ ./manage.py procrastinate healthchecks
Database connection: OK
Migrations: OK
Default Django Procrastinate App: OK
Worker App: OK
```

See {doc}`../production/monitoring` for more details on healthchecks.
