API Reference
=============

App
---

.. autoclass:: procrastinate.App
    :members: task, run_worker

Job stores
----------

.. autoclass:: procrastinate.PostgresJobStore

.. autoclass:: procrastinate.testing.InMemoryJobStore
    :members: reset

Tasks
-----
.. autoclass:: procrastinate.tasks.Task
    :members: defer, configure


Retry strategies
----------------

.. automodule:: procrastinate.retry

.. autoclass:: procrastinate.RetryStrategy

.. autoclass:: procrastinate.BaseRetryStrategy
    :members: get_schedule_in
