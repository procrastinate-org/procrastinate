Control the way synchronous calls to defer are handled
======================================================

When your app is synchronous (see `discussion-sync-defer`), you may want to
defer tasks purely synchronously.

``Psycopg2Connector``
---------------------

By setting your `App`'s connector to an instance of `Psycopg2Connector`, you will
get "classic" synchronous I/O. Note that in this case, the only thing you'll be
able to do synchronously is deferred tasks.

::

    import procrastinate

    app = procrastinate.App(
        connector=procrastinate.Psycopg2Connector(
            host="somehost",
        ),
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


Having multiple apps
--------------------

If you need to have multiple connectors interact with the tasks, you can
create multiple synchronized apps with `App.with_connector`::

    import procrastinate


    app = procrastinate.App(
        connector=procrastinate.AiopgConnector(...),
    )

    sync_app = app.with_connector(
        connector=procrastinate.Psycopg2Connector(...),
    )

If you do this, you can then register or defer tasks on either app.
