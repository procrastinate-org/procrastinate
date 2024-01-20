# Demos

This modules contains 3 mini-applications that showcase using
procrastinate in difference contexts:

- [demo_django]: a Django application,
- [demo_async]: an async application, it could be a
  FastAPI application, but to make things simpler, it's just a plain
  asyncio application.
- [demo_sync]: a synchronous application, similarily, it
  could be representative of a Flask application.

The demos are there both to showcase the code and as a way to easily
recreate the issues that are reported in the issues. They are not
production-ready code, and if you want to run them, you'll need to set
up the Procrastinate development environment (see
[contributing doc](contributing))

To run the demos, set PROCRATINATE_APP to
`procrastinate_demos.<demo_name>.app.app`, then run the
`procrastinate` CLI or `python -m procrastinate_demos.<demo_name>`
for the application main entrypoint.

For all apps, you'll need to have a PostgreSQL database running, and set
the `PG[...]` environment variables. This is taken care of by the
`. ./dev-env` script if you want to use it.

You'll need 2 terminals to run the demos, one for the procrastinate
worker and one for the application. (If you prefer, you can use
baclground processes).

## Async demo

Launch the worker in the first terminal:

```console
$ PROCRASTINATE_APP=procrastinate_demos.demo_async.app.app procrastinate worker
```

In the second terminal, run the application:

```console
$ python -m procrastinate_demos.demo_async
```

Defer a job by sending commands, as indicated by the application.

## Sync demo

Same with `sync`:

```console
$ PROCRASTINATE_APP=procrastinate_demos.demo_sync.app.app procrastinate worker
```

```console
$ python -m procrastinate_demos.demo_sync
```

## Django demo

In the first terminal, run the migrations, and then the Django server:

```console
$ procrastinate_demos/demo_django/manage.py migrate
$ procrastinate_demos/demo_django/manage.py runserver
```

In the second terminal, run the procrastinate worker:

```console
$ procrastinate_demos/demo_django/manage.py procrastinate worker
```

In your browser (`http://localhost:8000/`), you can now: - Create a
book - List books

When a book is created, it’s not “indexed” right away (there’s no real
indexing under the hood, it’s just for show). A first job is deferred to
index the book, which waits for 5 seconds and defers a second job. The
second job updates the book’s status to “indexed”. Reloading the list
page should show the book as indexed after about 5 seconds.
(The only reason why it's done in 2 jobs rather than one is to showcase
deferring a job from another job.)

(…Yes I’m not a frontend dev :) )

[demo_async]: https://github.com/procrastinate-org/procrastinate/tree/main/procrastinate_demos/demo_async/
[demo_django]: https://github.com/procrastinate-org/procrastinate/tree/main/procrastinate_demos/demo_django/
[demo_sync]: https://github.com/procrastinate-org/procrastinate/tree/main/procrastinate_demos/demo_sync/
