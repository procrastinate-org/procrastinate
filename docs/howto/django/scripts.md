# Running custom Django scripts

By default, `manage.py procrastinate` is the recommended way to run the worker
and other CLI commands. That said, if, for some reason, you want to run the
worker yourself, it's possible but slightly more convoluted.

The `DjangoConnector` configured on the default Procrastinate app cannot be
used to run the worker directly but the `DjangoConnector` provides a method to get a
suitable connector: `get_worker_connector()`.

The script below calls `django.setup()` manually. Alternatively, you can use
a [custom management command](https://docs.djangoproject.com/en/5.0/howto/custom-management-commands/)
in which case you don't need to call `django.setup()`.

```python
# myapp/worker.py
import django
from procrastinate.contrib.django import app

def main():
    django.setup()
    # By default, the app uses the Django database connection, which is unsuitable
    # for the worker.
    with app.replace_connector(app.connector.get_worker_connector()):
        app.run_worker()

if __name__ == "__main__":
    main()
```

:::{note}
The `.get_worker_connector()` method is only available on `DjangoConnector`
and the API isn't guaranteed to be completely stable yet.
Either `psycopg` or `aiopg` need to be installed for this to work.
`psycopg` will be used by default.
:::
