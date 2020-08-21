Create your connector
=====================

There are three ways you can specify the connection parameters:

Environment
-----------

You can use `libpq environment variables`_ (with ``PGPASSWORD`` or ``pgpass`` file):

.. code-block:: console

    $ export PGHOST=my.database.com  # Either export the variables in your shell
    $ PGPORT=5433 python -m myapp  # Or define the variables just for your process

and then define::

    import procrastinate
    procrastinate.AiopgConnector()

.. _`libpq environment variables`: https://www.postgresql.org/docs/current/libpq-envars.html


Data Source Name (DSN)
----------------------

You can use `aiopg dsn`_::

    import procrastinate
    procrastinate.AiopgConnector(dsn="postgres://user:password@host:port/dbname")

.. _`aiopg dsn`: https://aiopg.readthedocs.io/en/stable/core.html#aiopg.connect


Connection arguments
--------------------

You can use other `aiopg connection arguments`_ (which are the same as
`psycopg2 connection arguments`_)::

    import procrastinate
    procrastinate.AiopgConnector(user="user", password="password", host="host")

.. _`aiopg connection arguments`: https://aiopg.readthedocs.io/en/stable/core.html#aiopg.connect
.. _`psycopg2 connection arguments`: http://initd.org/psycopg/docs/module.html#psycopg2.connect

Other arguments
---------------

Apart from connection parameters, the `AiopgConnector` receives all the parameters from
the `aiopg.create_pool()`__.

.. __: https://aiopg.readthedocs.io/en/stable/core.html#aiopg.create_pool

What kind of Connector should I use?
------------------------------------

Procrastinate currently provides 2 connectors:

- `AiopgConnector`: Generic multipurpose connector. This should be the default.
- `Psycopg2Connector`: This connector is specialized for synchronous calls only, and
  should only be used to configure your app for synchronous multi-threaded applications
  that need to :term:`defer` tasks synchronously (see `discussion-sync-defer`).
