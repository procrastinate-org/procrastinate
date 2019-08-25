Launch a worker
---------------

You can either go towards the CLI route with:

.. code-block:: console

    $ procrastinate --verbose --app=dotted.path.to.app worker [queue [...]]

or, identically, use the code way::

    app.run_worker(queues=["queue", ...])

In both case, not specifying queues will tell Procrastinate to listen to every queue.
