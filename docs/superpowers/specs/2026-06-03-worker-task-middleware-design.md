# Task middleware — design

## Context

Procrastinate has no built-in way to run code around every task execution. Users
currently monkey-patch or wrap `@app.task` by hand. Two prior efforts exist:

- **Issue #1292** — the middleware feature discussion. It converged on: wrap the
  task *execution* (so middleware can see/modify the result), pass the `worker`
  so middleware can call `worker.stop()`, and explicitly *exclude* rate limiting
  (which belongs at the DB/fetch level, not at execution time).
- **PR #1317** — an implementation with two middleware kinds: a *worker*
  middleware (always async, runs on the event loop) and a *task* middleware
  (per-task, runs in the task's own thread for sync tasks).

The immediate motivation is downstream: the Django contrib needs to close Django's
per-thread DB connections **around every task, in the task's own thread** (sync
tasks open their ORM connection in the asgiref `sync_to_async` worker thread). A
clean middleware mechanism would let the contrib do this without subclassing `App`
or exposing a new public class (see the `DjangoApp` approach in PR #1555, which this
would eventually replace).

The key realization from PR #1317: its **worker** middleware runs on the event
loop — the *wrong thread* for a sync task's `close_old_connections()`. Its **task**
middleware runs in the right thread but is per-task, which would force the contrib
to intercept every registration. Neither combination is "global **and** in-thread,"
which is exactly what the Django case needs.

## Goal

Deliver a single, general-purpose **in-context task middleware** mechanism:

- runs **in the task's execution context** — in the worker thread for sync tasks,
  on the event loop for async tasks;
- registrable **per-task** and **worker-wide** (global), as **lists** (chains);
- expressive enough for the #1292 use cases (logging/OpenTelemetry, DI containers,
  async timeouts on async tasks, `worker.stop()`), via native `with`/`async with`;
- sufficient for a future Django consumer to do global, in-thread connection
  cleanup with no `App` subclass.

### Non-goals (explicitly deferred, all additive later)

- An **event-loop `worker_middleware` chain** (always-async, wraps the whole job on
  the loop). The only thing it would add over this design is *async* middleware
  around *sync* tasks (awaiting async resources / `async with` / thread-free
  gating). The name `worker_middleware` is reserved so it can be added with zero
  breakage.
- **Rate limiting** — orthogonal; belongs at the DB/fetch level (per #1292).
- **`JobContext` replacement** by middleware (`call_next()` takes no args in v1).
- **Innermost `start_timestamp`** (measuring task-only duration) — see B1 below.
- **The Django consumer itself** — reimplementing connection cleanup as a
  worker-wide sync+async middleware pair is a *follow-up* PR depending on this one.

## Design

### Concept

A middleware is a callable wrapping one task's execution:

```python
# sync task → sync middleware (runs in the task's worker thread)
def my_mw(call_next, context, worker):
    with some_span(context.task.name):
        return call_next()

# async task → async middleware (runs on the worker event loop)
async def my_mw(call_next, context, worker):
    async with some_async_resource():
        return await call_next()
```

It receives `(call_next, context, worker)`, must call/await `call_next()` to run the
next middleware (or the task), and returns the result. It may run code before/after,
use context managers, catch/transform exceptions, modify the result, and call
`worker.stop()`.

### The sync/async rule

A middleware's sync/async nature **must match the task it wraps** — that is what
allows the sync middleware to execute *in the sync task's thread*:

- a **sync** (`def`) middleware applies to **sync** tasks;
- a **coroutine** (`async def`) middleware applies to **async** tasks;
- to cover both kinds globally, register one of each (this is how the future Django
  cleanup ships: a sync variant + an async variant).

Classification uses `inspect.iscoroutinefunction`, also checking `__call__` for
callable objects and unwrapping `functools.partial`.

### Scopes & naming

Two scopes, both **lists**:

- **Per-task:** `@app.task(task_middleware=[mw_a, mw_b])`
- **Worker-wide:** `app.run_worker(task_middleware=[mw_x])`,
  `run_worker_async(task_middleware=...)`, or
  `worker_defaults={"task_middleware": [...]}`.

The name `task_middleware` is used identically in all three places (explicit, and
symmetric with the reserved future `worker_middleware`).

### Ordering

Effective chain for a task, **outermost → innermost**:

```
[worker-wide middlewares matching the task's sync/async kind]   (outermost)
  → [all per-task middlewares for this task]                    (validated to match)
    → task function                                             (innermost)
```

Worker-wide outermost means a global cleanup/telemetry middleware wraps everything,
including per-task middleware — required so the Django cleanup closes the connection
*after* any per-task DB work.

### Enforcement (strict vs filter)

- **Per-task** — validated at **registration** (`Task.__init__`): every middleware's
  kind must match the task; otherwise raise a `ProcrastinateError` immediately at
  import. (A mismatch is always a bug: a sync middleware can't `await call_next()`
  for an async task, and an async middleware can't run in a sync task's thread.)
- **Worker-wide** — no error; **filtered by compatibility** per task (sync
  middlewares wrap sync tasks, async wrap async). A mixed list is the expected way
  to cover both kinds. Optionally emit a one-time `debug` log noting middlewares
  skipped for a task due to kind mismatch.

### Execution model

- **Async task:** matching middlewares are composed and `await`ed on the event loop
  around the task coroutine.
- **Sync task:** matching middlewares are composed into one zero-arg callable and the
  *entire composed callable (middlewares + task)* is run via a **single**
  `utils.sync_to_async(...)` — so the whole chain runs in **one worker thread**, the
  same thread the task's DB connection lives in.

Composition helper (`procrastinate/middleware.py`), outermost = first:

```python
def compose(middlewares, run_task, context, worker):
    call_next = run_task
    for mw in reversed(middlewares):
        call_next = functools.partial(mw, call_next, context, worker)
    return call_next   # zero-arg: composed() for sync, await composed() for async
```

`ensure_async` in `worker._process_job` becomes (sketch):

```python
job_args = [context] if task.pass_context else []
is_async = inspect.iscoroutinefunction(task.func)
mws = self._resolve_task_middlewares(task, is_async)   # worker-wide(compatible) + per-task

if is_async:
    async def run_task():
        return await task.func(*job_args, **job.task_kwargs)
    task_result = await compose(mws, run_task, context, self)()
else:
    def run_task():
        return task(*job_args, **job.task_kwargs)
    task_result = await utils.sync_to_async(compose(mws, run_task, context, self))

if inspect.isawaitable(task_result):     # existing sync-returns-awaitable handling, kept
    task_result = await task_result
```

`_resolve_task_middlewares(task, is_async)` returns
`[m for m in self.task_middleware if is_async_mw(m) == is_async] + (task.task_middleware or [])`.

**No-op guarantee:** with an empty effective chain, `compose` returns `run_task`
unchanged, so the sync path is exactly today's `await sync_to_async(task)` and the
async path is exactly today's `await task(...)` — behaviorally identical to current
behavior, with no semantic change and negligible overhead when no middleware is
configured.

### `worker.stop()` thread-safety

`stop()` currently does `self._stop_event.set()` on an `asyncio.Event`, which is
unsafe from a sync middleware running in a thread. Fix: capture the loop in `run()`
(`self._loop = asyncio.get_running_loop()`) and have `stop()` use
`self._loop.call_soon_threadsafe(self._stop_event.set)` when called off the loop
thread. (Also fixes the same latent issue in PR #1317.)

### Timestamps (decision B1)

`context.start_timestamp` is set when the job is fetched, before middleware runs, so
a middleware's "before" work counts toward the job's logged duration. **We keep this
(B1)** — simplest, matches today, middleware overhead is normally negligible, and it
avoids muddying `start_timestamp` semantics for `pass_context` tasks. Measuring
task-only duration (B2) is deferred.

## Semantics & edge cases

- **Outcome:** the chain runs inside `_process_job`'s existing `try/except`. Catch &
  return → job succeeds; propagate → existing retry/`FAILED`/`ABORTED` logic. A
  middleware that swallows `JobAborted`/`CancelledError` is the author's
  responsibility. Sync-task cancellation keeps today's caveat (the thread runs to
  completion).
- **Result:** the outermost middleware's return value becomes `job_result.result`.
- **`pass_context`:** the task still receives `context` first; middleware also gets
  it as the 2nd parameter.
- **Builtin tasks:** worker-wide middleware wraps all tasks the worker runs,
  including builtin (e.g. `remove_old_jobs`); middleware may skip via
  `context.task.name`.

## Files to change

- **add** `procrastinate/middleware.py` — `TaskMiddleware` type alias (with sync &
  async forms) and the generic, shared `compose` / `is_async_middleware` helpers.
  (Names are `task_`-prefixed where kind-specific so a future `WorkerMiddleware`
  slots in cleanly; `compose`/`is_async_middleware` stay generic.)
- **edit** `procrastinate/tasks.py` — `Task` gains `task_middleware`; validate
  kind-match in `__init__`.
- **edit** `procrastinate/blueprints.py` — `task()` overloads accept
  `task_middleware`, threaded into `Task`.
- **edit** `procrastinate/app.py` — `WorkerOptions` gains `task_middleware`; doc it
  on `run_worker_async`.
- **edit** `procrastinate/worker.py` — `Worker.__init__` accepts `task_middleware`;
  `_resolve_task_middlewares`; rewrite `ensure_async`; capture loop in `run()`;
  thread-safe `stop()`.
- **edit** `docs/howto/advanced/middleware.md` — document `task_middleware`
  (per-task + worker-wide), the sync/async rule, ordering, examples (telemetry, DI,
  `worker.stop()`); note `worker_middleware` reserved/future.
- **edit** `docs/reference.rst` — document `procrastinate.middleware` (`compose`,
  `is_async_middleware`).
- **add** `tests/unit/test_middleware.py` and acceptance coverage (see below).

## Testing plan

- **Unit:** compose order (outer→inner); sync chain + task share one thread (assert
  `threading.get_ident()`); async chain on the loop; per-task mismatch **raises** at
  registration; worker-wide **filters** by kind; empty chain = identity (no-op);
  result transformation; exception propagation; `worker.stop()` from a sync
  middleware thread actually stops the worker; multiple middlewares nest correctly.
- **Acceptance:** a real worker run with a recording middleware over both a sync and
  an async task, asserting before/after ordering; stop-from-middleware.

## Future work (additive, non-breaking)

- Event-loop `worker_middleware` chain (reserved name) for async-wrapping of sync
  tasks / thread-free gating.
- Django connection-cleanup consumer (verified feasible): a worker-wide sync+async
  `task_middleware` pair that ports PR #1555's `close_old_connections()` /
  `reset_queries()` logic — the sync middleware runs in the task's worker thread,
  the async one via `sync_to_async(thread_sensitive=True)`. Injected through
  `create_app`'s `worker_defaults["task_middleware"]` on a **plain**
  `procrastinate.App`, retiring the `DjangoApp` subclass *and* its public export
  from PR #1555. Caveat: `worker_defaults` is overridden (not merged) if a user
  passes `task_middleware=` to a custom `run_worker()` call (not possible via
  `manage.py procrastinate worker`); mitigate by exporting the middleware and/or
  appending it in the management command.
- Rate limiting as a separate DB/fetch-level feature.
- B2 innermost `start_timestamp`; `JobContext` replacement.
