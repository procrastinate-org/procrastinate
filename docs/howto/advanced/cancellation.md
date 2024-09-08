# Cancel a job

We can cancel a job that has not yet been processed by a worker. We can also
mark a job that is currently being processed for abortion, but this request
has to be handled by the task itself.

## Cancel a job (that is not being processed yet)

```python
# by using the sync method
app.job_manager.cancel_job_by_id(33)
# or by using the async method
await app.job_manager.cancel_job_by_id_async(33)
```

## Delete the cancelled job

A cancelled job can also be deleted from the database.

```python
# by using the sync method
app.job_manager.cancel_job_by_id(33, delete_job=True)
# or by using the async method
await app.job_manager.cancel_job_by_id_async(33, delete_job=True)
```

## Mark a running job for abortion

If a worker has not picked up the job yet, the below command behaves like the
command without the `abort` option. But if a job is already running, the `abort` option marks this job for abortion (see below
how to handle this request).

```python
# by using the sync method
app.job_manager.cancel_job_by_id(33, abort=True)
# or by using the async method
await app.job_manager.cancel_job_by_id_async(33, abort=True)
```

Behind the scenes, the worker receives a Postgres notification every time a job is requested to abort, (unless `listen_notify=False`).

The worker also polls (respecting `polling_interval`) the database for abortion requests, as long as the worker is running at least one job (in the absence of running job, there is nothing to abort).

:::{note}
When a job is requested to abort and that job fails, it will not be retried (regardless of the retry strategy).
:::

## Handle an abortion request inside the task

### Sync tasks

In a sync task, we can check (for example, periodically) if the task should be
aborted. If we want to respect that abortion request (we don't have to), we raise a
`JobAborted` error. Any message passed to `JobAborted` (e.g.
`raise JobAborted("custom message")`) will end up in the logs.

```python
@app.task(pass_context=True)
def my_task(context):
  for i in range(100):
    if context.should_abort():
      raise exceptions.JobAborted
    do_something_expensive()
```

### Async tasks

For async tasks (coroutines), they are cancelled via the [asyncio cancellation](https://docs.python.org/3/library/asyncio-task.html#task-cancellation) mechasnism.

```python
@app.task()
async def my_task():
  do_something_synchronous()
  # if the job is aborted while it waits for do_something to complete, asyncio.CancelledError will be raised here
  await do_something()
```

It is possible to prevent the job from aborting by capturing asyncio.CancelledError.

```python
@app.task()
async def my_task():
    try:
      important_task = asyncio.create_task(something_important())
      # shield something_important from being cancelled
      await asyncio.shield(important_task)
    except asyncio.CancelledError:
      # capture the error and waits for something important to complete
      await important_task
      # if the job should be marked as aborted, rethrow. Otherwise continue for job to succeed
```
