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

## Mark a currently being processed job for abortion

If a worker has not picked up the job yet, the below command behaves like the
command without the `abort` option. But if a job is already in the middle of
being processed, the `abort` option marks this job for abortion (see below
how to handle this request).

```python
# by using the sync method
app.job_manager.cancel_job_by_id(33, abort=True)
# or by using the async method
await app.job_manager.cancel_job_by_id_async(33, abort=True)
```

## Handle a abortion request inside the task

In our task, we can check (for example, periodically) if the task should be
aborted. If we want to respect that request (we don't have to), we raise a
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

There is also an async API

```python
@app.task(pass_context=True)
async def my_task(context):
  for i in range(100):
    if await context.should_abort_async():
      raise exceptions.JobAborted
    do_something_expensive()
```

:::{warning}
`context.should_abort()` and `context.should_abort_async()` does poll the
database and might flood the database. Ensure you do it only sometimes and
not from too many parallel tasks.
:::

:::{note}
When a task of a job that was requested to be aborted raises an error, the job
is marked as failed (regardless of the retry strategy).
:::
