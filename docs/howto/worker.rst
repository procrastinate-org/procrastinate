Launch a worker
---------------

You can either go towards the CLI route with:

.. code-block:: console

    $ procrastinate --verbose --app=dotted.path.to.app worker [--name=worker-name] [queue [...]]

or, identically, use the code way::

    app.run_worker(queues=["queue", ...], name="worker-name")
    # or
    await app.run_worker_async(queues=["queue", ...], name="worker-name")

In both cases, not specifying queues will tell Procrastinate to listen to every queue.
Naming the worker is optional.

.. note::

    `App.run_worker` will take care of launching an event loop, opening the app,
    running the worker, and when it exists, closing the app and the event loop.

    On the other hand, `App.run_worker_async` needs to run while the app is open.
    The CLI takes care of opening the app.
