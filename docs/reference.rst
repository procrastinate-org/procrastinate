API Reference
=============

App
---

.. autoclass:: procrastinate.App
    :members: task, run_worker, configure_task

App.builtin_tasks
"""""""""""""""""
Builtin tasks are registered when the App object is initialized, and
are accessible through :py:attr:`App.builtin_tasks`:

.. code-block:: python

    app.builtin_tasks["remove_old_jobs"].defer(max_hours=72)


Job stores
----------

.. autoclass:: procrastinate.PostgresJobStore

.. autoclass:: procrastinate.testing.InMemoryJobStore
    :members: reset

Tasks
-----
.. autoclass:: procrastinate.tasks.Task
    :members: defer, defer_async, configure


Builtin tasks
-------------

Procrastinate has builtin tasks that are all available from the CLI:

.. _remove_old_jobs_reference:

.. autofunction:: procrastinate.builtin_tasks.remove_old_jobs(max_hours, queue=None, remove_error=False)


Retry strategies
----------------

.. automodule:: procrastinate.retry

.. autoclass:: procrastinate.RetryStrategy

.. autoclass:: procrastinate.BaseRetryStrategy
    :members: get_schedule_in
