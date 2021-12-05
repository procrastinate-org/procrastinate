Delete finished jobs
====================

Delete jobs on completion
-------------------------

By passing an extra parameter, you can make workers automatically delete jobs right
when they are finished::

    app = procrastinate.App(worker_defaults={"delete_jobs": "always"})
    # or when launching a worker:
    app.run_worker(delete_jobs="always")

With ``always``, every finished job will be deleted on completion. Other options are:

- ``successful`` to only delete successful jobs and keep failed jobs in the database
  until explicit deletion.
- ``never`` to keep every job in the database, this is the default.

You can also do this from the CLI::

    procrastinate worker --delete-jobs=always


Delete older jobs
-----------------

You may want to clean your database by deleting old jobs. Procrastinate exposes
a builtin task which lets you do just that. Note that jobs and linked events
will be irreversibly removed from the database when running this task.

From the CLI
^^^^^^^^^^^^

.. code-block:: console

    $ procrastinate defer builtin:procrastinate.builtin_tasks.remove_old_jobs max_hours=72

For more information about this task's parameter,
see :py:func:`~procrastinate.builtin_tasks.remove_old_jobs`

If you launch ``remove_old_jobs`` from a cron you may want to avoid inserting a new job
when there is one already waiting in the queue. You can rely on a :term:`queueing locks
<queueing lock>` for that:

.. code-block:: console

    $ procrastinate defer --queueing-lock=remove_old_jobs --ignore-already-enqueued \
        procrastinate_builtin_tasks.remove_old_jobs max_hours=72

See also the `periodic launch <cron>` section for related information.

In Python code
^^^^^^^^^^^^^^

Import the following module:

.. code-block:: python

    from procrastinate import builtin_tasks

Then:

.. code-block:: python

    builtin_tasks.remove_old_jobs.defer(max_hours=72)

You can access the builtin task through ``procrastinate.builtin_tasks``.
The parameters are the same than when accessing the task through the CLI.

For example, to use a queueing lock:

.. code-block:: python

    deferrer = builtin_tasks.remove_old_jobs.configure(queueing_lock="remove_old_jobs")
    deferrer.defer(max_hours=72)

The call to ``defer`` will raise an `AlreadyEnqueued` exception if there already is
a "remove_old_jobs" job waiting in the queue, which you may want to catch and ignore.

As mentioned in the previous section you may want to run ``remove_old_jobs``
periodically. For that you may use a Unix cron, or rely on Procrastinate's "periodic
tasks" functionality. This is how you can make ``remove_old_jobs`` periodic:

.. code-block:: python

    @app.periodic(cron="0 4 * * *")
    @app.task(queueing_lock="remove_old_jobs", pass_context=True)
    async def remove_old_jobs(context, timestamp):
        return await builtin_tasks.remove_old_jobs(
            context=context,
            max_hours=72,
            remove_error=True,
        )

With this you define your own ``remove_old_jobs`` task, which relies on Procrastinate's
builtin ``remove_old_jobs`` task function. The task is periodic, and configured to be
deferred every day at 4 am.
