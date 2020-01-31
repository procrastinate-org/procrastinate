Launch a worker
---------------

You can either go towards the CLI route with:

.. code-block:: console

    $ procrastinate --verbose --app=dotted.path.to.app worker [--name=worker-name] [queue [...]]

or, identically, use the code way::

    app.run_worker(queues=["queue", ...], name="worker-name")

In both cases, not specifying queues will tell Procrastinate to listen to every queue.
Naming the worker is optional.
