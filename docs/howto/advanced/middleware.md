# Middleware for workers and tasks

## Worker middleware

Procrastinate lets you extend a worker's behavior by adding a custom middleware.
This middleware wraps the execution of every task assigned to the worker, allowing
you to execute custom logic before and after each task runs. You might use it to
log task activity, measure performance, or handle errors consistently.

```python
def custom_middleware(process_task, context, worker):
    # Execute any logic before the task runs
    result = await process_task()
    # Execute any logic after the task runs
    return result

app.run_worker(middleware=custom_middleware)
```

The middleware is coroutine that takes three arguments:
- `process_task`: a coroutine (without arguments) that runs the task
- `context`: a `JobContext` object that contains information about the job
- `worker`: the worker that runs the job

The middleware should await `process_task` to run the task and return the result.

:::{note}
The `worker` instance can be used to stop the worker from the middleware by
calling `worker.stop()`. This will stop the worker after the jobs currently being
processed are finished.
:::

:::{warning}
When the middleware is called, the job is already fetched from the database and
in `doing` state. After the `process_task` coroutine is called the job is still
in `doing` state and will be updated after the middleware returns.
:::

## Task middleware

You can also add a middleware to a specific task. This middleware will only wrap
the execution of this specific task then.


:::{note}
For a sync task, the middleware should be a sync function. For an async task, the
middleware should be a coroutine.
:::

```python
# for a sync task
def custom_sync_middleware(process_task, context, worker):
    # do something at the beginning of the task
    result = process_task()
    # do something at the end of the task
    return result

@app.task(middleware=custom_sync_middleware)
def my_task():
    ...

# or for an async task
async def custom_async_middleware(process_task, context, worker):
    # do something at the beginning of the task
    result = await process_task()
    # do something at the end of the task
    return result

@app.task(middleware=custom_async_middleware)
async def my_task():
    ...
```

::: {warning}
Just like with worker middleware, when the task middleware is executed, the job has already been fetched from the database and is in `doing` state. The final state of the job will only be updated once the middleware has fully completed its execution.
:::
