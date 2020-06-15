Control the way synchronous calls to defer are handled
======================================================

In some cases, usually linked to multi-threading (see `discussion-sync-defer`), you may
want to defer tasks purely synchronously (what is called "classic" synchronous I/O).
There are two ways to achieve this:

``real_sync_defer=True``
------------------------

By building your `AiopgConnector` with ``real_sync_defer=True``, defer operations will
automatically be handled by a synchronous connector, based on ``psycopg2``::

    import procrastinate

    app = procrastinate.App(
        connector=procrastinate.AiopgConnector(
            host="somehost",
            real_sync_defer=True
        ),
    )

``Psycopg2Connector``
---------------------

By setting your `App`'s connector to an instance of `Psycopg2Connector`, you will also
get "classic" synchronous I/O. Note that in this case, some ``App`` features will be
unavailable, such as the ``admin`` and ``worker`` sub-commands.

It is perfectly fine to give the App either kind of connectors depending on the
situation.

How does it work?
-----------------

In both cases, the synchronous connector will use a
``psycopg2.pool.ThreadedConnectionPool`` (see psycopg2 documentation__), which should
fit most workflows.

.. __: https://www.psycopg.org/docs/pool.html#psycopg2.pool.ThreadedConnectionPool


.. note::

    If you use ``real_sync_defer``, the ``ThreadedConnectionPool`` will be instantiated
    mostly with the parameters passed to the `AiopgConnector`. That being said, there
    are small differences here and there between the two parameter sets. If you find a
    parameter that is not well supported, feel free to warn us through an issue__.

.. __: https://github.com/peopledoc/procrastinate/issues
