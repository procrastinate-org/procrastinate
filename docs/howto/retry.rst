Define a retry strategy on a task
---------------------------------

We sometimes know in advance that a task may fail randomly. For example a task
fetching resources on another network. You can define a retry strategy on a
task and Procrastinate will enforce it.

Note that a job waiting to be retried lives in the database. It will persist across
app / machine reboots.

Simple strategies
^^^^^^^^^^^^^^^^^

- Retry 5 times (so 6 attempts total)::

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

Advanced strategies let you:

- define a maximum number of retries (if you don't, jobs will be retried indefinitely
  until they pass)
- define the retry delay, with constant, linear and exponential backoff options (if
  you don't, jobs will be retried immediately)
- define the exception types you want to retry on (if you don't, jobs will be retried
  on any type of exceptions)

Define your precise strategy using a `RetryStrategy` instance::

    from procrastinate import RetryStrategy

    @app.task(retry=procrastinate.RetryStrategy(
        max_attempts=10,
        wait=5,
        retry_exceptions={ConnectionError, IOError}
    ))
    def my_other_task():
        print("Hello world")

`RetryStrategy` takes 3 parameters related to how long it will wait
between retries:

- ``wait=5`` to wait 5 seconds before each retry
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

        def get_schedule_in(self, *, exception:Exception, attempts: int, **kwargs) -> int:
            if attempts >= max_attempts:
                return None

            return random.uniform(self.min, self.max)


It's interesting to add a catch-all parameter ``**kwargs`` to make your strategy more
resilient to possible changes of Procrastinate in the future.
