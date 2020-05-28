Execute multiple jobs at the same time
======================================

By default, each worker only takes one job at a time. One of the ways to increase
your processing throughput is to launch multiple workers, each using their own
process.

But Procrastinate supports asynchronous tasks, and the main idea behind asynchronous
code is to have concurrency: while a job is waiting for external I/O (usually network),
the CPU is free to run other jobs. That is why Procrastinate workers are able to
launch multiple asynchronous :term:`sub-workers <Sub-worker>`.

You can do this either from Python::

    app.run_worker(concurrency=30)

Or from the command line:

.. code-block:: console

    $ procrastinate worker --concurrency=30

The discussion section contains a few important guidelines regarding asynchronous
concurrency (see `discussion-async`).
