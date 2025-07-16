# Define a retry strategy on a task

We sometimes know in advance that a task may fail randomly. For example a task
fetching resources on another network. You can define a retry strategy on a
task and Procrastinate will enforce it.

Note that a job waiting to be retried lives in the database. It will persist across
app / machine reboots.

## Simple strategies

-   Retry 5 times (so 6 attempts total):

    ```python
    @app.task(retry=5)
    def flaky_task():
        if random.random() > 0.9:
            raise Exception("Who could have seen this coming?")
        print("Hello world")
    ```

-   Retry indefinitely:

    ```python
    @app.task(retry=True)
    def flaky_task():
        if random.random() > 0.9:
            raise Exception("Who could have seen this coming?")
        print("Hello world")
    ```

## Advanced strategies

Advanced strategies let you:

-   define a maximum number of retries (if you don't, jobs will be retried indefinitely
    until they pass)
-   define the retry delay, with constant, linear and exponential backoff options (if
    you don't, jobs will be retried immediately)
-   define the exception types you want to retry on (if you don't, jobs will be retried
    on any type of exceptions)

Define your precise strategy using a {py:class}`RetryStrategy` instance:

```python
from procrastinate import RetryStrategy

@app.task(retry=procrastinate.RetryStrategy(
    max_attempts=10,
    wait=5,
    retry_exceptions={ConnectionError, IOError}
))
def my_other_task():
    print("Hello world")
```

{py:class}`RetryStrategy` takes 3 parameters related to how long it will wait
between retries:

-   `wait=5` to wait 5 seconds before each retry
-   `linear_wait=5` to wait 5 seconds then 10 then 15 and so on
-   `exponential_wait=5` to wait 5 seconds then 25 then 125 and so on

## Implementing your own strategy

If you want to go for a fully fledged custom retry strategy, you can implement your
own retry strategy by returning a `RetryDecision` object from the
`get_retry_decision` method. This also allows to (optionally) change the priority,
the queue or the lock of the job. If `None` is returned from `get_retry_decision`
then the job will not be retried.

The time to wait between retries can be specified with `retry_in` or alternatively
with `retry_at`. This is similar to how `schedule_in` and `schedule_at` are used
when {doc}`scheduling a job in the future <schedule>`.

```python
import random
from procrastinate import Job, RetryDecision

class RandomRetryStrategy(procrastinate.BaseRetryStrategy):
    max_attempts = 3
    min = 1
    max = 10

    def get_retry_decision(self, *, exception:Exception, job:Job) -> RetryDecision:
        if job.attempts >= max_attempts:
            return RetryDecision(should_retry=False)

        wait = random.uniform(self.min, self.max)

        return RetryDecision(
            retry_in={"seconds": wait}, # or retry_at (a datetime object)
            priority=job.priority + 1, # optional
            queue="another_queue", # optional
            lock="another_lock", # optional
        )
```

There is also a legacy `get_schedule_in` method that is deprecated an will be
removed in a future version in favor of the above `get_retry_decision` method.

## Knowing whether a job is on its last attempt

By using `pass_context=True`, and introspecting the task's retry strategy,
you can know whether a currently executing job is on its last attempt:

```python
@app.task(retry=10, pass_context=True)
def my_task(job_context: procrastinate.JobContext) -> None:
	job = job_context.job
	task = job_context.task
    if task.retry.get_retry_decision(exception=Exception(), job=job) is None:
        print("Warning: last attempt!")

    if random.random() < 0.9:
        raise Exception
```

# Retry a Job Manually

Sometimes a manual retry, for instance, after we fix an integration's configuration, can be practical.
This is why the job_manager offers an API to do so. Retrying a `failed` job will set the status of the job
back to `todo` while keeping the history of events in place. The action of retrying a failed job,
is also recording a new Event of type `retried`.

## Retry a job programatically

```python
app.job_manager.retry_job_by_id(
    job.id, utils.utcnow(), job.priority, job.queue_name, job.lock
)
# or by using the async method
await app.job_manager.retry_job_by_id_async(
    job.id, utils.utcnow(), job.priority, job.queue_name, job.lock
)
```

## For django users

An admin action `Retry Failed Job` can also be invoked from the table view of the
Procrastinate Jobs.
