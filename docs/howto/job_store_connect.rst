Create your job store, and connect to a PostgreSQL database
-----------------------------------------------------------

There are three ways you can specify the connection parameters:

- You can use `libpq environment variables`_ (with ``PGPASSWORD`` or ``pgpass`` file):

.. code-block:: console

    $ export PGHOST=my.database.com  # Either export the variables in your shell
    $ PGPORT=5433 python -m myapp  # Or define the variables just for your process

  and then just define::

    import procrastinate
    procrastinate.PostgresConnector()

.. _`libpq environment variables`: https://www.postgresql.org/docs/current/libpq-envars.html

- You can use `aiopg dsn`_::

    import procrastinate
    procrastinate.PostgresConnector(dsn="postgres://user:password@host:port/dbname")

.. _`aiopg dsn`: https://aiopg.readthedocs.io/en/stable/core.html#aiopg.connect

- You can use other `aiopg connection arguments`_ (which are the same as
  `psycopg2 connection arguments`_)::

    import procrastinate
    procrastinate.PostgresConnector(user="user", password="password", host="host")

.. _`aiopg connection arguments`: https://aiopg.readthedocs.io/en/stable/core.html#aiopg.connect
.. _`psycopg2 connection arguments`: http://initd.org/psycopg/docs/module.html#psycopg2.connect
