(sync-defer)=

# Control the way synchronous calls to defer are handled

When your app is synchronous (see {ref}`discussion-async`), you may want to
defer tasks synchronously.
In most cases, if you set up an asynchronous connector, Procrastinate will
automatically select the right connector for you. However, you can also
explicitly set up a synchronous connector.

## `SyncPsycopgConnector`

By setting your {py:class}`App`'s connector to an instance of {py:class}`SyncPsycopgConnector` (or
any other synchronous connector), you will get "classic" synchronous I/O. Note
that in this case, the only thing you'll be able to do is defer tasks. Other
operations trigger an error with a synchronous connector.

```
import procrastinate

app = procrastinate.App(
    connector=procrastinate.SyncPsycopgConnector(
        host="somehost",
    ),
)
```

{py:class}`SyncPsycopgConnector` uses a `psycopg_pool.ConnectionPool` (see psycopg
[documentation](https://www.psycopg.org/psycopg3/docs/api/pool.html#psycopg_pool.ConnectionPool)).

## `Psycopg2Connector`

The {py:class}`Psycopg2Connector` is a connector that uses a
`psycopg2_pool.ThreadedConnectionPool`. It used to be the default connector,
but {py:class}`SyncPsycopgConnector` is now the preferred option. There is no plan to
deprecate {py:class}`Psycopg2Connector`.

## `SQLAlchemyPsycopg2Connector`

If you use SQLAlchemy in your synchronous application, you may want to use an
{py:class}`SQLAlchemyPsycopg2Connector` from the `contrib.sqlalchemy` module instead. The
advantage over using a {py:class}`Psycopg2Connector` is that Procrastinate can use the same
SQLAchemy engine (and connection pool) as the rest of your application, thereby
minimizing the number of database connections.

```
from sqlalchemy import create_engine

from procrastinate import App
from procrastinate.contrib.sqlalchemy import SQLAlchemyPsycopg2Connector

engine = create_engine("postgresql+psycopg2://", echo=True)

app = App(connector=SQLAlchemyPsycopg2Connector())
app.open(engine)
```

## Having multiple apps

If you need to have multiple connectors interact with the tasks, you can
create multiple synchronized apps with {py:meth}`App.with_connector`:

```
import procrastinate


app = procrastinate.App(
    connector=procrastinate.PsycopgConnector(...),
)

sync_app = app.with_connector(
    connector=procrastinate.SyncPsycopgConnector(...),
)
```

## Procrastinate's automatic connector selection

Async connectors are able to summon their synchronous counterpart when needed
(using `BaseConnector.get_sync_connector`).

All sync operations in Procrastinate (so mainly deferring tasks synchronously)
will request the synchronous connector from the async connector under the hood.

:::{note}
If you're relying on this mechanism, note the following mechanism:

If you request the synchronous connector before opening the app, you will
be using a synchronous connector.

If you request the synchronous connector after opening the app, you will get
the asynchronous connector, with a compatibility layer to make synchronous
operations. This will only work if you call it inside a function decorated
with `asgiref.sync.sync_to_async` (such as inside a sync job). Otherwise,
you will likely get a `RuntimeError`.
:::
