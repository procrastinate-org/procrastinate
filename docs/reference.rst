API Reference
=============

App
---

.. autoclass:: cabbage.App
    :members: task, run_worker

Job stores
----------

.. autoclass:: cabbage.PostgresJobStore

.. autoclass:: cabbage.testing.InMemoryJobStore
    :members: reset

Retry strategies
----------------

.. automodule:: cabbage.retry

.. autoclass:: cabbage.RetryStrategy

.. autoclass:: cabbage.BaseRetryStrategy
    :members: get_schedule_in
