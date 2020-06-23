Limit the number of opened connections
======================================

By default, each worker using an `AiopgConnector` will open up to 10 parallel
connections. You can control this value with the ``maxsize`` parameter (from
`aiopg.create_pool()`__)(see `discussions-pool-size`)

.. __: https://aiopg.readthedocs.io/en/stable/core.html#aiopg.create_pool

Disabling the ``LISTEN/NOTIFY`` feature (see `discussion-general`) will use one less
connection per worker::

    app = procrastinate.App(worker_defaults={"listen_notify": False})
    # or when launching a worker:
    app.run_worker(listen_notify=False)

This works from the command line too:

.. code-block:: console

    procrastinate worker --no-listen-notify

Finally, setting the ``maxsize`` argument of the `AiopgConnector` to ``1`` will also
disable the LISTEN/NOTIFY feature, but you will receive a warning.
