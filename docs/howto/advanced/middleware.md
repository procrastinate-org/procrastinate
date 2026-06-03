# Add task middleware

A *task middleware* wraps the execution of a task, letting you run code before and
after it — for logging, dependency-injection scopes, resource cleanup, and so on.

A middleware is a callable taking `(call_next, context, worker)`. It must call (or
`await`) `call_next()` to run the next middleware — or the task itself — and return
the result. `context` is the {py:class}`~procrastinate.JobContext`; `worker` is the
running worker (you may call `worker.stop()` from it).

## The sync/async rule

A middleware's nature must match the task it wraps:

- a **sync** task takes **sync** middleware (a plain `def`), which runs in the
  task's worker thread;
- an **async** task takes **async** middleware (`async def`), which runs on the
  worker's event loop.

```python
# sync task -> sync middleware
def log_mw(call_next, context, worker):
    print(f"starting {context.task.name}")
    try:
        return call_next()
    finally:
        print(f"finished {context.task.name}")

# async task -> async middleware (async def, awaits call_next())
async def async_log_mw(call_next, context, worker):
    print(f"starting {context.task.name}")
    try:
        return await call_next()
    finally:
        print(f"finished {context.task.name}")
```

## Per-task middleware

```python
@app.task(task_middleware=[log_mw])
def my_task():
    ...
```

A mismatch (an async middleware on a sync task, or vice versa) raises an error when
the task is declared.

## Worker-wide middleware

Apply middleware to every task a worker runs:

```python
app.run_worker(task_middleware=[log_mw, async_log_mw])
```

Worker-wide middleware is **filtered by kind** per task: the sync ones wrap sync
tasks, the async ones wrap async tasks. To cover both kinds, pass one of each (as
above). Worker-wide middleware wraps *around* any per-task middleware.

## Ordering

For a given task, the chain is, outermost to innermost: worker-wide middleware (in
list order) → per-task middleware (in list order) → the task function. The first
middleware in a list runs its "before" code first and its "after" code last.

## Stopping the worker

A middleware can stop the worker (after currently-running jobs finish):

```python
def stop_after_one(call_next, context, worker):
    worker.stop()
    return call_next()
```

:::{note}
Task middleware as described here runs in the task's own execution context.
A *worker middleware* (running on the event loop, allowing `async with` /
`await` around sync tasks) may be added in the future.
:::
