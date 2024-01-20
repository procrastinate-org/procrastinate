# Limit the number of opened connections

By default, each worker using an {any}`AiopgConnector` will open up to 10 parallel
connections. You can control this value with the `max_size` parameter (from
[psycopg_pool.ConnectionPool()](https://www.psycopg.org/psycopg3/docs/api/pool.html))(see {any}`discussions-pool-size`)

Disabling the `LISTEN/NOTIFY` feature (see {any}`discussion-general`) will use one less
connection per worker:

```
app = procrastinate.App(worker_defaults={"listen_notify": False})
# or when launching a worker:
app.run_worker(listen_notify=False)
```

This works from the command line too:

```console
procrastinate worker --no-listen-notify
```
