Instantiate your connector
==========================

What kind of Connector should I use?
------------------------------------

Procrastinate currently provides 5 connectors:

Two async connector:

- `PsycopgConnector`: Asynchronous connector based on psycopg v3.
- `AiopgConnector`: Asynchronous connector based on aiopg.

Three sync connectors, that may only be used for deferring jobs.

- `SyncPsycopgConnector`: Synchronous connector based on psycopg v3.
- `Psycopg2Connector`: Synchronous connector based on psycop2.
- `SQLAlchemyPsycopg2Connector`: This connector is specialized for SQLAlchemy
  applications. It should be used if you want to use SQLAlchemy to manage your
  database connection and share your connection pool with the rest of your app.
  It should only be used for deferring jobs, not for running them.

.. note::

    More details on sync connectors can be found in the :ref:`sync-defer` section.

In order to use Procrastinate, you will need an asynchronous connector, even if
your application is synchronous. In most cases, the asynchronous connectors
should be able to run in both asynchronous and synchronous contexts, but the
synchronous connector can only be used in synchronous contexts.

There are 2 main things you will do with a connector: defer jobs, and run the worker.
The worker can only be run with an asynchronous connector, but you can defer jobs
with either asynchronous and synchronous connectors.

How to instantiate a connector?
--------------------------------

There are three ways you can specify the connection parameters:

Environment
~~~~~~~~~~~

You can use `libpq environment variables`_ (with ``PGPASSWORD`` or ``pgpass`` file):

.. code-block:: console

    $ export PGHOST=my.database.com  # Either export the variables in your shell
    $ PGPORT=5433 python -m myapp  # Or define the variables just for your process

and then define::

    import procrastinate
    app = procrastinate.App(connector=procrastinate.PsycopgConnector())

.. _`libpq environment variables`: https://www.postgresql.org/docs/current/libpq-envars.html


Data Source Name (DSN)
~~~~~~~~~~~~~~~~~~~~~~

You can use `libpq connection string`_::

    import procrastinate
    app = procrastinate.App(
      connector=procrastinate.PsycopgConnector(
        conninfo="postgres://user:password@host:port/dbname"
      )
    )

.. _`libpq connection string`: https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING


Connection arguments
~~~~~~~~~~~~~~~~~~~~

You can use other `psycopg connection arguments`_::

    import procrastinate
    procrastinate.PsycopgConnector(
        kwargs={
            "dbname": "dbname",
            "user"="user",
            "password"="password",
            "host"="host",
        }
    )

.. _`psycopg connection arguments`: https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING-KEYWORD-VALUE

Note that the specifics of the arguments depend on the connector you are using.
Please refer to the documentation of the connector you are using for more details.

Other arguments
~~~~~~~~~~~~~~~

Apart from connection parameters, the `PsycopgConnector` can handle all the
parameters from the `psycopg_pool.AsyncConnectionPool()`__ function.

.. __: https://www.psycopg.org/psycopg3/docs/api/pool.html#psycopg_pool.AsyncConnectionPool


Similarly, the `SyncPsycopgConnector` can handle all the parameters from the
`psycopg_pool.ConnectionPool()`__ function.

.. __: https://www.psycopg.org/psycopg3/docs/api/pool.html#psycopg_pool.ConnectionPool
