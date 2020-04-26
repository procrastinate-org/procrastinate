.. _remove_old_jobs:

Remove old jobs
---------------

You may want to clean your database by removing old jobs. Procrastinate exposes
a builtin task which lets you do just that. Note that jobs and linked events
will be irreversibly removed from the database when running this task.

From the CLI
^^^^^^^^^^^^

.. code-block:: console

    $ procrastinate defer procrastinate.builtin_tasks.remove_old_jobs max_hours=72

For more information about this task's parameter,
see :py:func:`~procrastinate.builtin_tasks.remove_old_jobs`

In Python code
^^^^^^^^^^^^^^

.. code-block:: python

    app.builtin_tasks["remove_old_jobs"].defer(max_hours=72)

You can access the builtin task through :py:attr:`App.builtin_tasks`.
The parameters are the same than when accessing the task through the CLI.
