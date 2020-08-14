Find a correct place for your app
---------------------------------

We advise you to place your app in one of the following places:

- Your program ``__init__`` or the place where you define your top level objects,
- A dedicated module (``yourapp.procrastinate`` for example),
- The place where you define all your tasks if it's a single module.

In the first two cases, it's important to specify the location to your tasks using the
``import_paths`` parameter::

    import procrastinate

    app = procrastinate.App(
        connector=connector,
        import_paths=["dotted.path.to", "all.the.modules", "that.define.tasks"]
    )

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


Open the app and automatically close it with a context manager
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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

Or with a context manager::

   with procrastinate.App(connector=connector).open() as app:
       pass

For async case::

   app = await procrastinate.App(connector=connector).open_async()

Or with a context manager::

   async with procrastinate.App(connector=connector).open_async() as app:
       pass

Open the app, and let the garbage collector terminate the connection
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The app does not necessarily need to be closed at the end of your program. Indeed, the
connections to the database will be automatically terminated when the database
connector is garbage collected. Thus, your program can work with only the following
statements, as we did in the readme and the quickstart::

   app = procrastinate.App(connector=connector)
   app.open()

Use an external pool instead of the connectors default pool
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The database connectors instantiate their own connection pool by default. You can
overwrite this behavior and supply your own pool, passing it as an argument to the
``open`` and ``open_async`` functions.
