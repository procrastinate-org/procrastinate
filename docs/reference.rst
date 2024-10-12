API Reference
=============

App
---

.. autoclass:: procrastinate.App
    :members: open, open_async, task, run_worker, run_worker_async, configure_task,
              from_path, add_tasks_from, add_task_alias, with_connector, periodic,
              tasks, job_manager

Connectors
----------
.. autoclass:: procrastinate.PsycopgConnector

.. autoclass:: procrastinate.SyncPsycopgConnector

.. autoclass:: procrastinate.contrib.aiopg.AiopgConnector

.. autoclass:: procrastinate.contrib.psycopg2.Psycopg2Connector

.. autoclass:: procrastinate.testing.InMemoryConnector
    :members: reset, jobs

Tasks
-----
.. autoclass:: procrastinate.tasks.Task
    :members: defer, defer_async, configure, name, aliases, retry_strategy,
              pass_context, queue, lock, queueing_lock

When tasks are created with argument ``pass_context``, they are provided a
`JobContext` argument:

.. autoclass:: procrastinate.JobContext
    :members: app, worker_name, worker_queues, job

Blueprints
----------

.. autoclass:: procrastinate.blueprints.Blueprint
    :members: task, periodic, add_tasks_from, add_task_alias


Builtin tasks
-------------

Procrastinate has builtin tasks that are all available from the CLI.
For all tasks, the context argument will be passed automatically.
The name of the tasks will be: ``builtin:procrastinate.builtin.<task_name>``

.. automodule:: procrastinate.builtin_tasks
    :members:

Jobs
----

.. autoclass:: procrastinate.jobs.Job
    :members:


Retry strategies
----------------

.. automodule:: procrastinate.retry

.. autoclass:: procrastinate.RetryStrategy

.. autoclass:: procrastinate.BaseRetryStrategy
    :members: get_retry_decision, get_schedule_in

.. deprecated:: 2.9
    The `get_schedule_in` method is deprecated.

.. autoclass:: procrastinate.RetryDecision


Exceptions
----------

.. automodule:: procrastinate.exceptions
    :members: ProcrastinateException, LoadFromPathError,
              ConnectorException, AlreadyEnqueued, AppNotOpen, TaskNotFound,
              UnboundTaskError

Job statuses
------------

.. autoclass:: procrastinate.jobs.Status
    :members:


Accessing the jobs in the Database
----------------------------------

.. autoclass:: procrastinate.manager.JobManager
    :members:

Django
------

.. automodule:: procrastinate.contrib.django


SQLAlchemy
----------

.. autoclass:: procrastinate.contrib.sqlalchemy.SQLAlchemyPsycopg2Connector
