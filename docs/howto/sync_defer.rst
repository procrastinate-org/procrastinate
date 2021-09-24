Control the way synchronous calls to defer are handled
======================================================

In some cases, usually linked to multi-threading (see `discussion-sync-defer`), you may
want to defer tasks purely synchronously (what is called "classic" synchronous I/O).

``Psycopg2Connector``
---------------------

By setting your `App`'s connector to an instance of `Psycopg2Connector`, you will
get "classic" synchronous I/O. Note that in this case, some ``App`` features will be
unavailable, such as the ``shell`` and ``worker`` sub-commands::

    import procrastinate

    app = procrastinate.App(
        connector=procrastinate.Psycopg2Connector(
            host="somehost",
        ),
    )

It is perfectly fine to give the App either kind of connectors depending on the
situation::

    import sys, procrastinate

    # This is an example condition, you'll need to check that it works in your case
    if sys.argv[0:2] == ["procrastinate", "worker"]:
        connector_class = procrastinate.AiopgConnector
    else:
        connector_class = procrastinate.Psycopg2Connector

    app = procrastinate.App(
        connector=connector_class(host="somehost"),
    )


How does it work?
~~~~~~~~~~~~~~~~~

The synchronous connector will use a ``psycopg2.pool.ThreadedConnectionPool`` (see
psycopg2 documentation__), which should fit most workflows.

.. __: https://www.psycopg.org/docs/pool.html#psycopg2.pool.ThreadedConnectionPool


``SQLAlchemyPsycopg2Connector``
-------------------------------

If you use SQLAlchemy in your synchronous application, you may want to use an
`SQLAlchemyPsycopg2Connector` from the ``contrib.sqlalchemy`` module instead. The
advantage over using a `Psycopg2Connector` is that Procrastinate can use the same
SQLAchemy engine (and connection pool) as the rest of your application, thereby
minimizing the number of database connections.

::

    from sqlalchemy import create_engine

    from procrastinate import App
    from procrastinate.contrib.sqlalchemy import SQLAlchemyPsycopg2Connector

    engine = create_engine("postgresql+psycopg2://", echo=True)

    app = App(connector=SQLAlchemyPsycopg2Connector())
    app.open(engine)
