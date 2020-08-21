Initiate and terminate the connection to the database
-----------------------------------------------------

The app must be opened at the beginning of the program to create the connection pool to
the database, and eventually closed to properly terminate it.

The app implements several ways to do this.

Explicitly open and close the app
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The app can be opened using the ``open`` method (for sync case) or ``open_async``
method (for async case). It eventually needs to be closed, using the ``close`` method
(for sync case) or ``close_async`` (for async case).

For sync case::

    app.open()
    ...
    app.close()

For async case::

    await app.open_async()
    ...
    await app.close_async()


Open and close the app with a context manager
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The app can be opened with a context manager, which will automatically close it when
leaving the context.

For sync case::

    with app.open():
        pass

For async case::

    async with app.open_async():
        pass


Create and open the app in a single line
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Both ``open`` and ``open_async`` return the current app when they are called or
entered, which allows you to instantiate and open your app in a single line.

For sync case::

   app = procrastinate.App(connector=connector).open()


Open the app, and let the garbage collector terminate the connection
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The app does not necessarily need to be closed at the end of your program. The
connections to the database will be automatically terminated when the database
connector is garbage collected. Thus, your program can work with only the following
statements, as we did in the readme and the quickstart::

   app = procrastinate.App(connector=connector)
   app.open()

But remember: "explicit is better than implicit".

Use an external pool instead of the connectors default pool
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The database connectors instantiate their own connection pool by default. You can
overwrite this behavior and supply your own pool, passing it as an argument to the
``open`` and ``open_async`` functions.
