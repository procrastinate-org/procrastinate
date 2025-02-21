# Middleware for workers and tasks

Procrastinate lets you add middleware to workers and tasks. Middleware is a
function that wraps the execution of a task, allowing you to execute custom
logic before and after the task runs. You might use it to log task activity,
measure performance, or handle errors consistently.

A middleware is a function or coroutine (see examples below) that takes three arguments:
- `process_task`: a function resp. coroutine (without arguments) that runs the task
- `context`: a `JobContext` object that contains information about the job
- `worker`: the worker that runs the job

The middleware should call resp. await `process_task` to run the task and then return the
result.

:::{note}
The `worker` instance can be used to stop the worker from within the middleware by
calling `worker.stop()`. This will stop the worker after the jobs currently being
processed by the worker are finished.
:::

:::{warning}
When the middleware is called, the job was already fetched from the database and
is in `doing` state. After `process_task` the job is still in `doing` state and will
be updated to its final state after the middleware returns.
:::

## Worker middleware

To add a middleware to a worker, pass a middleware coroutine to the `run_worker` or
`run_worker_async` method. The middleware will wrap the execution of all tasks
run by this worker.

```python
async def custom_worker_middleware(process_task, context, worker):
    # Execute any logic before the task is processed
    result = await process_task()
    # Execute any logic after the task is processed
    return result

app.run_worker(middleware=custom_middleware)
```

## Task middleware

You can also add a middleware to a specific task. This middleware will only wrap
the execution of this task then.

:::{note}
For a sync task, the middleware must be a sync function, and for an async task, the
middleware should be a coroutine.
:::

```python
# middleware of a sync task
def custom_sync_middleware(process_task, context, worker):
    # Execute any logic before the task is processed
    result = process_task()
    # Execute any logic after the task is processed
    return result

@app.task(middleware=custom_sync_middleware)
def my_task():
    ...

# or middleware of an async task
async def custom_async_middleware(process_task, context, worker):
    # Execute any logic before the task is processed
    result = await process_task()
    # Execute any logic after the task is processed
    return result

@app.task(middleware=custom_async_middleware)
async def my_task():
    ...
```
