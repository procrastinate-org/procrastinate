# Add middleware

*Middleware* wraps the execution of your tasks, letting you run code before and
after each one — for logging, tracing, dependency-injection scopes, resource
cleanup, and so on.

Procrastinate has two kinds of middleware:

- **Task middleware** runs *in the task's own execution context* — a sync
  middleware in the task's worker thread, an async middleware on the event loop —
  so it must match the task's sync/async nature. Register it per-task or
  worker-wide.
- **Worker middleware** is *always async* and wraps every job on the event loop,
  both sync and async tasks. Register it worker-wide only.

Both are callables taking `(call_next, context, worker)`. A middleware must call
(or `await`) `call_next()` to run the next middleware — or the task itself — and
return the result. `context` is the {py:class}`~procrastinate.JobContext`;
`worker` is the running worker (you may call `worker.stop()` from it).

## Task middleware

A task middleware wraps a task's execution in the task's own context.

### The sync/async rule

A task middleware's nature must match the task it wraps:

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

A middleware's kind is detected with {py:func}`inspect.iscoroutinefunction`: if
you build a middleware out of wrappers or decorators, keep the outermost
callable an `async def` for it to count as async middleware.

### Per-task middleware

```python
@app.task(task_middleware=[log_mw])
def my_task():
    ...
```

A mismatch (an async middleware on a sync task, or vice versa) raises
{py:class}`~procrastinate.exceptions.MiddlewareKindMismatch` when the task is
declared.

### Worker-wide task middleware

Apply task middleware to every task a worker runs:

```python
app.run_worker(task_middleware=[log_mw, async_log_mw])
```

Worker-wide task middleware is **filtered by kind** per task: the sync ones wrap
sync tasks, the async ones wrap async tasks. To cover both kinds, pass one of each
(as above). Worker-wide task middleware wraps *around* any per-task middleware.

### Ordering

For a given task, the task-middleware chain is, outermost to innermost: worker-wide
task middleware (in list order) → per-task middleware (in list order) → the task
function. The first middleware in a list runs its "before" code first and its
"after" code last.

## Worker middleware

A *worker middleware* is **always async** and wraps every job a worker runs **on
the event loop** — both sync and async tasks. (For a sync task, `await call_next()`
drives the task's worker-thread hop internally.) Unlike task middleware there is no
sync/async kind to match, and it is registered **worker-wide only**.

```python
async def otel_mw(call_next, context, worker):
    with tracer.start_as_current_span(f"run/{context.task.name}"):
        return await call_next()   # the task's exception propagates → span records it

app.run_worker(worker_middleware=[otel_mw])
```

It can also be set on `worker_defaults`. When the worker is created, a non-callable
entry raises `TypeError`, and a sync (non-async) entry raises
{py:class}`~procrastinate.exceptions.MiddlewareKindMismatch`.

A worker middleware is the **outermost** layer. For a given job the full chain is,
outermost to innermost: worker middleware → worker-wide task middleware → per-task
task middleware → the task.

### Worker middleware vs. worker-wide task middleware

Both are registered on the worker, so pick by what you need:

- **Worker middleware** (`worker_middleware=`) — always async, runs on the event
  loop, wraps every task uniformly (sync and async). Use it to wrap a job in async
  code: a tracing span, an `async with`, async metrics.
- **Worker-wide task middleware** (`task_middleware=`) — runs *in the task's own
  context* (a sync middleware in the task's worker thread) and is kind-matched.
  Running in the task's thread is what lets it manage thread-local state around a
  sync task. This is how Procrastinate's {doc}`Django integration
  <../django/basic_usage>` closes Django's per-thread DB connections after each
  task.

## Failures and retries

This applies to **both** task and worker middleware. Exceptions raised by the task
(or by an inner middleware) flow through the chain to the worker, which uses them to
decide the job's final status: retries, failure, and abortion
({py:class}`~procrastinate.exceptions.JobAborted`) all rely on the exception
reaching the worker. A middleware that swallows exceptions (e.g. with a bare
`except Exception:`) would mark the job succeeded, skip retries, and ignore abort
requests — run cleanup code in a `try`/`finally` block and always re-raise.

## Stopping the worker

Any middleware can stop the worker (after currently-running jobs finish, subject
to `shutdown_graceful_timeout`) by calling `worker.stop()`:

```python
def stop_after_one(call_next, context, worker):
    worker.stop()
    return call_next()
```
