API Reference
=============

App
---

.. autoclass:: procrastinate.App
    :members: open, open_async, task, run_worker, run_worker_async, configure_task,
              from_path

Connectors
----------

.. autoclass:: procrastinate.AiopgConnector

.. autoclass:: procrastinate.Psycopg2Connector

.. autoclass:: procrastinate.testing.InMemoryConnector
    :members: reset

Tasks
-----
.. autoclass:: procrastinate.tasks.Task
    :members: defer, defer_async, configure

When tasks are created with argument ``pass_context``, they are provided a
`JobContext` argument:

.. autoclass:: procrastinate.JobContext
    :members: app, worker_name, worker_queues, job, task

Builtin tasks
-------------

Procrastinate has builtin tasks that are all available from the CLI.
For all tasks, the context argument will be passed automatically.

.. automodule:: procrastinate.builtin_tasks
    :members:

Jobs
----

.. autoclass:: procrastinate.jobs.Job


Retry strategies
----------------

.. automodule:: procrastinate.retry

.. autoclass:: procrastinate.RetryStrategy

.. autoclass:: procrastinate.BaseRetryStrategy
    :members: get_schedule_in


Exceptions
----------

.. automodule:: procrastinate.exceptions
    :members: ProcrastinateException, LoadFromPathError,
              ConnectorException, AlreadyEnqueued, AppNotOpen

Administration
--------------

.. autoclass:: procrastinate.admin.Admin
    :members: list_jobs, list_jobs_async, list_queues, list_queues_async,
              list_tasks, list_tasks_async, set_job_status, set_job_status_async
