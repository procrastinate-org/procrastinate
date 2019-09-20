Create your job store, and connect to a PostgreSQL database
-----------------------------------------------------------

There are three ways you can specify the connection parameters:

- You can use `libpq environment variables`_ (with ``PGPASSWORD`` or pgpass file)::

    $ export PGHOST=my.database.com  # Either export the variables in your shell
    $ PGPORT=5433 python -m myapp  # Or define the variables just for your process

  and then just define::

    import procrastinate
    procrastinate.PostgresJobStore()

.. _`libpq environment variables`: https://www.postgresql.org/docs/current/libpq-envars.html

- You can use `psycopg2 dsn`_::

    import procrastinate
    procrastinate.PostgresJobStore(dsn="postgres://user:password@host:port/dbname")

.. _`psycopg2 dsn`: http://initd.org/psycopg/docs/module.html#psycopg2.connect

- You can use other `psycopg2 connection arguments`_::

    import procrastinate
    procrastinate.PostgresJobStore(user="user", password="password", host="host")

.. _`psycopg2 connection arguments`: http://initd.org/psycopg/docs/module.html#psycopg2.connect
