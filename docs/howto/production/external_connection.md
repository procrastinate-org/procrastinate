# Using an external database connection

Procrastinate supports deferring jobs on an externally-managed database connection.
This lets you insert the job within the same transaction as your own database
operations, enabling patterns like the **transactional outbox**. Cancelling a job
and reading its status can run on an external connection too.

## When to use this

If you need the job to be created **atomically** with other database writes (e.g.
inserting a row into your own table and deferring a task that processes it), pass your
connection to `configure(connection=...)`. The job INSERT will execute on your
connection, inside your transaction. You are responsible for committing.

## Sync example (psycopg)

```python
import psycopg
from procrastinate import App, SyncPsycopgConnector

app = App(connector=SyncPsycopgConnector(conninfo="..."))
app.open()

@app.task
def process_order(order_id):
    ...

with psycopg.connect("...") as conn:
    conn.autocommit = False
    conn.execute("INSERT INTO orders (id, ...) VALUES (%s, ...)", [42])
    process_order.configure(connection=conn).defer(order_id=42)
    conn.commit()  # both the order row and the job are committed together
```

## Async example (psycopg)

```python
import psycopg
from procrastinate import App, PsycopgConnector

app = App(connector=PsycopgConnector(conninfo="..."))
await app.open_async()

@app.task
def process_order(order_id):
    ...

async with await psycopg.AsyncConnection.connect("...") as conn:
    conn.autocommit = False
    await conn.execute("INSERT INTO orders (id, ...) VALUES (%s, ...)", [42])
    await process_order.configure(connection=conn).defer_async(order_id=42)
    await conn.commit()
```

## SQLAlchemy example

```python
from procrastinate import App
from procrastinate.contrib.sqlalchemy import SQLAlchemyPsycopg2Connector

connector = SQLAlchemyPsycopg2Connector(dsn="postgresql+psycopg2:///mydb")
app = App(connector=connector)
app.open()

@app.task
def process_order(order_id):
    ...

with connector.engine.connect() as conn:
    conn.exec_driver_sql("INSERT INTO orders (id) VALUES (%s)", [42])
    process_order.configure(connection=conn).defer(order_id=42)
    conn.commit()
```

## Cancelling jobs and reading status

`cancel_job_by_id` / `cancel_job_by_id_async` and `get_job_status` /
`get_job_status_async` accept the same `connection` argument. Useful if you update
your own tables when cancelling a job and want both changes to commit (or roll back)
together:

```python
async with await psycopg.AsyncConnection.connect("...") as conn:
    await conn.execute("UPDATE orders SET state = 'cancelled' WHERE id = %s", [42])
    await app.job_manager.cancel_job_by_id_async(job_id, connection=conn)
    await conn.commit()  # the order update and the cancellation commit together
```

## Supported connectors

- `SyncPsycopgConnector` — pass a `psycopg.Connection`
- `PsycopgConnector` — pass a `psycopg.AsyncConnection`
- `SQLAlchemyPsycopg2Connector` — pass a `sqlalchemy.engine.Connection`

Other connectors will raise a `ConnectorException` if `connection` is provided.

## Important notes

- **NOTIFY is delayed**: The database NOTIFY that wakes workers fires when you
  commit. This is expected and acceptable. The same applies when cancelling a
  running job with `abort=True`: the worker only sees the abort request once you
  commit.
- **Error handling**: Errors from the job INSERT (e.g. queueing lock violations)
  are wrapped as usual via procrastinate's exception hierarchy, but they may abort
  your transaction. Use savepoints if you need to isolate the defer from the rest
  of your transaction.
- **No validation**: Procrastinate does not validate the connection type. Passing
  the wrong type will produce a runtime error from the database driver.
