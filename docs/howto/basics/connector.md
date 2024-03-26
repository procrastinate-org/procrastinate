# Instantiate your connector

## What kind of Connector should I use?

Procrastinate currently provides 5 connectors:

Two async connector:

- {py:class}`PsycopgConnector`: Asynchronous connector based on psycopg v3.
- {py:class}`AiopgConnector`: Asynchronous connector based on aiopg.

Three sync connectors, that may only be used for deferring jobs.

- {py:class}`SyncPsycopgConnector`: Synchronous connector based on psycopg v3.
- {py:class}`Psycopg2Connector`: Synchronous connector based on psycop2.
- {py:class}`SQLAlchemyPsycopg2Connector`: This connector is specialized for SQLAlchemy
  applications. It should be used if you want to use SQLAlchemy to manage your
  database connection and share your connection pool with the rest of your app.
  It should only be used for deferring jobs, not for running them.

:::{note}
More details on sync connectors can be found in the {ref}`sync-defer` section.
:::

In order to use Procrastinate, you will need an asynchronous connector, even if
your application is synchronous. In most cases, the asynchronous connectors
should be able to run in both asynchronous and synchronous contexts, but the
synchronous connector can only be used in synchronous contexts.

There are 2 main things you will do with a connector: defer jobs, and run the worker.
The worker can only be run with an asynchronous connector, but you can defer jobs
with either asynchronous and synchronous connectors.

## How to instantiate a connector?

There are three ways you can specify the connection parameters:

### Environment

You can use [libpq environment variables] (with `PGPASSWORD` or `pgpass` file):

```console
$ export PGHOST=my.database.com  # Either export the variables in your shell
$ PGPORT=5433 python -m myapp  # Or define the variables just for your process
```

and then define:

```
import procrastinate
app = procrastinate.App(connector=procrastinate.PsycopgConnector())
```

### Data Source Name (DSN)

You can use [libpq connection string]:

```
import procrastinate
app = procrastinate.App(
  connector=procrastinate.PsycopgConnector(
    conninfo="postgres://user:password@host:port/dbname"
  )
)
```

### Connection arguments

You can use other [psycopg connection arguments]:

```
import procrastinate
procrastinate.PsycopgConnector(
    kwargs={
        "dbname": "dbname",
        "user"="user",
        "password"="password",
        "host"="host",
    }
)
```

Note that the specifics of the arguments depend on the connector you are using.
Please refer to the documentation of the connector you are using for more details.

### Other arguments

Apart from connection parameters, the {py:class}`PsycopgConnector` can handle all the
parameters from the [psycopg_pool.AsyncConnectionPool()](https://www.psycopg.org/psycopg3/docs/api/pool.html#psycopg_pool.AsyncConnectionPool) function.

Similarly, the {py:class}`SyncPsycopgConnector` can handle all the parameters from the
[psycopg_pool.ConnectionPool()](https://www.psycopg.org/psycopg3/docs/api/pool.html#psycopg_pool.ConnectionPool) function.

### Custom connection pool

It's possible to use custom connection pool with {py:class}`PsycopgConnector`. It
accepts `pool_factory` keyword argument. You can pass any callable that returns
{py:class}`psycopg_pool.AsyncConnectionPool` instance:

```
import procrastinate
import psycopg_pool
app = procrastinate.App(
  connector=procrastinate.PsycopgConnector(
    pool_factory=psycopg_pool.AsyncNullConnectionPool,
    conninfo="postgres://user:password@host:port/dbname",
  )
)
```

In this case, {py:class}`AsyncNullConnectionPool` receives `conninfo` keyword argument
and creates null connection pool (which effectively disables pooling). This is useful
when you use [PgBouncer] or some other external pooler in order to resolve pooling outside
of your application.

[libpq connection string]: https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING
[libpq environment variables]: https://www.postgresql.org/docs/current/libpq-envars.html
[psycopg connection arguments]: https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING-KEYWORD-VALUE
[PgBouncer]: https://www.pgbouncer.org/
