.. _retry:

Define a retry strategy on a task
---------------------------------

We sometimes know in advance that a task may fail randomly. For example a task
fetching resources on another network. You can define a retry strategy on a
task and Procrastinate will enforce it.

Note that a job waiting to be retried lives in the database. It will persist across
app / machine reboots.

Simple strategies
^^^^^^^^^^^^^^^^^

- Define a number of attempts::

    @app.task(retry=5)
    def flaky_task():
        if random.random() > 0.9:
            raise Exception("Who could have seen this coming?")
        print("Hello world")


- Retry indefinitely::

    @app.task(retry=True)
    def flaky_task():
        if random.random() > 0.9:
            raise Exception("Who could have seen this coming?")
        print("Hello world")


Advanced strategies
^^^^^^^^^^^^^^^^^^^

You can get a more precise strategy using a :py:class:`RetryStrategy` instance::

    from procrastinate import RetryStrategy

    @app.task(retry=procrastinate.RetryStrategy(max_attempts=10, wait=5))
    def my_other_task():
        print("Hello world")

:py:class:`RetryStrategy` takes 3 parameters related to how much it will wait
between retries:

- ``wait=5`` to wait 5 seconds between each retry
- ``linear_wait=5`` to wait 5 seconds then 10 then 15 and so on
- ``exponential_wait=5`` to wait 5 seconds then 25 then 125 and so on

Implementing your own strategy
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- If you want to go for a fully fledged custom retry strategy, you can implement your
  own retry strategy (though we recommend always keeping a max_retry)::

    import random

    class RandomRetryStrategy(procrastinate.BaseRetryStrategy):
        max_attempts = 3
        min = 1
        max = 10

        def get_schedule_in(self, attempts: int) -> int:
            if attempts >= max_attempts:
                return None

            return random.uniform(self.min, self.max)

