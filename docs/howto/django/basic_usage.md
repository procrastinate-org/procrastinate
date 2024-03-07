# Use Procrastinate in a Django application

## Defining tasks

Add your tasks to `tasks.py` in your Django app.
Inside tasks, you can use the classical ORM API or the [async ORM API] to access your models.

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
$ (venv) ./manage.py procrastinate worker
```

`./manage.py procrastinate` mostly behaves like the `procrastinate` command
itself, with some commands removed and the app is configured for you.
Apart from `worker`, subcommands such as `defer` are supported.

:::{note}
Procrastinate generates a fully async connector for you using a `Psycopg` (by
default) or `Aiopg` connector depending on whether `psycopg` version 3 or
`aiopg` is installed, and connects using the `DATABASES` settings. If neither
library is installed, an error will be raised.
:::

See {doc}`../basics/command_line` for more details on the CLI.
If you prefer writing your own scripts, see {doc}`scripts`.

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
[async orm api]: https://docs.djangoproject.com/en/4.2/topics/async/#queries-the-orm
