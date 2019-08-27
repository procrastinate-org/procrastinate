Define a retry strategy on a task
---------------------------------

We sometimes know in advance that a task may fail randomly. For example a task
fetching resources on another network. You can define a retry strategy on a
task and Procrastinate will enforce it.
Available strategies are:

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

- You can get a more precise strategy using a RetryStrategy instance::

    from procrastinate import RetryStrategy

    @app.task(retry=procrastinate.RetryStrategy(max_attempts=10, wait=5))
    def my_other_task():
        print("Hello world")

- If you want to go for a fully fledged custom retry strategy, you can implement your
  own retry strategy::

    class MyRetryStrategy(procrastinate.BaseRetryStrategy):
        growth: Optional[str] = "linear"

        def get_schedule_in(self, attempts: int) -> int:
            if super().get_schedule_in(attempts) is None:
                return None

            if self.growth == "linear":
                return self.wait * attempts
            elif self.growth == "exponential":
                ...

Note that a job waiting to be retried lives in the database. It will persist across
app / machine reboots.
