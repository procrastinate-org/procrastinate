# Task Middleware Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an in-context "task middleware" mechanism — a chain of callables that wraps each task's execution in the task's own context (the worker thread for sync tasks, the event loop for async tasks), registrable per-task and worker-wide.

**Architecture:** A new `procrastinate/middleware.py` provides a `compose()` helper and an `is_async_middleware()` classifier. `Task` stores per-task middleware and validates kind-match at registration. The worker resolves the effective chain (worker-wide compatible + per-task) and runs it; for sync tasks the whole chain+task is wrapped in one `utils.sync_to_async` so it shares a thread. `worker.stop()` is made thread-safe so a sync middleware can call it.

**Tech Stack:** Python 3.9+, asgiref `sync_to_async`, pytest / pytest-asyncio (mode=auto), `procrastinate.testing.InMemoryConnector`.

**Spec:** `docs/superpowers/specs/2026-06-03-worker-task-middleware-design.md`

> **IMPORTANT — no commits.** The project owner asked to work **without committing**. Do **not** run `git commit`/`git add`. Each task ends at a green test run; leave all changes in the working tree for review.

---

## File structure

- **Create** `procrastinate/middleware.py` — types, `is_async_middleware`, `compose`.
- **Modify** `procrastinate/exceptions.py` — add `MiddlewareKindMismatch`.
- **Modify** `procrastinate/tasks.py` — `Task` gains `task_middleware`, validated in `__init__`.
- **Modify** `procrastinate/blueprints.py` — `task()` overloads + impl accept `task_middleware`.
- **Modify** `procrastinate/app.py` — `WorkerOptions` gains `task_middleware`; document it.
- **Modify** `procrastinate/worker.py` — `Worker.__init__` accepts `task_middleware`; `_resolve_task_middlewares`; rewrite `ensure_async`; capture loop in `run()`; thread-safe `stop()`.
- **Modify** `docs/howto/advanced/middleware.md` and `docs/reference.rst`.
- **Create** `tests/unit/test_middleware.py`.

---

## Task 1: middleware module (`compose` + classifier)

**Files:**
- Create: `procrastinate/middleware.py`
- Test: `tests/unit/test_middleware.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/unit/test_middleware.py`:

```python
from __future__ import annotations

import functools

from procrastinate import middleware


def test_compose_empty_returns_run_task_unchanged():
    def run_task():
        return "task"

    composed = middleware.compose([], run_task, context=None, worker=None)
    assert composed is run_task
    assert composed() == "task"


def test_compose_orders_outermost_first():
    calls = []

    def run_task():
        calls.append("task")
        return "result"

    def make_mw(label):
        def mw(call_next, context, worker):
            calls.append(f"before:{label}")
            result = call_next()
            calls.append(f"after:{label}")
            return result

        return mw

    composed = middleware.compose(
        [make_mw("a"), make_mw("b")], run_task, context=None, worker=None
    )
    assert composed() == "result"
    assert calls == [
        "before:a",
        "before:b",
        "task",
        "after:b",
        "after:a",
    ]


def test_is_async_middleware_detects_sync_and_async():
    def sync_mw(call_next, context, worker): ...

    async def async_mw(call_next, context, worker): ...

    assert middleware.is_async_middleware(sync_mw) is False
    assert middleware.is_async_middleware(async_mw) is True


def test_is_async_middleware_handles_partials_and_callables():
    async def async_mw(call_next, context, worker, extra): ...

    assert middleware.is_async_middleware(functools.partial(async_mw, extra=1)) is True

    class AsyncCallable:
        async def __call__(self, call_next, context, worker): ...

    assert middleware.is_async_middleware(AsyncCallable()) is True
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/unit/test_middleware.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'procrastinate.middleware'`

- [ ] **Step 3: Write `procrastinate/middleware.py`**

```python
from __future__ import annotations

import functools
import inspect
from collections.abc import Awaitable, Callable, Sequence
from typing import TYPE_CHECKING, Any, Union

if TYPE_CHECKING:
    from procrastinate import job_context, worker

# A *task* middleware wraps one task's execution. It receives a zero-arg
# ``call_next`` (the next middleware, or the task itself), the JobContext and the
# Worker, and must call/await ``call_next()`` and return the result.
#
# A sync task middleware wraps a sync task (and runs in the task's worker thread);
# an async task middleware wraps an async task (and runs on the event loop).
#
# (A future "worker middleware" — always-async, wrapping the whole job on the loop
# — will be added to this module with its own ``WorkerMiddleware`` type. The
# ``compose`` and ``is_async_middleware`` helpers below are generic and shared.)
SyncCallNext = Callable[[], Any]
AsyncCallNext = Callable[[], Awaitable[Any]]
SyncTaskMiddleware = Callable[
    [SyncCallNext, "job_context.JobContext", "worker.Worker"], Any
]
AsyncTaskMiddleware = Callable[
    [AsyncCallNext, "job_context.JobContext", "worker.Worker"], Awaitable[Any]
]
TaskMiddleware = Union[SyncTaskMiddleware, AsyncTaskMiddleware]


def is_async_middleware(middleware: TaskMiddleware) -> bool:
    """
    Whether a middleware is a coroutine function (and thus wraps async tasks).
    Handles plain functions, ``functools.partial`` and callable objects.
    """
    if inspect.iscoroutinefunction(middleware):
        return True
    call = getattr(middleware, "__call__", None)
    return bool(call is not None and inspect.iscoroutinefunction(call))


def compose(
    middlewares: Sequence[Callable[..., Any]],
    run_task: Callable[[], Any],
    context: job_context.JobContext | None,
    worker: worker.Worker | None,
) -> Callable[[], Any]:
    """
    Nest ``middlewares`` around ``run_task``, first item outermost. Returns a
    zero-arg callable: call it for sync tasks, await its result for async tasks.
    An empty sequence returns ``run_task`` unchanged (no-op).

    Generic and shared: ``middlewares`` may be ``TaskMiddleware`` now, or the
    future ``WorkerMiddleware`` chain — this helper only nests callables of shape
    ``(call_next, context, worker)``.
    """
    call_next = run_task
    for middleware in reversed(list(middlewares)):
        call_next = functools.partial(middleware, call_next, context, worker)
    return call_next
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/unit/test_middleware.py -v`
Expected: PASS (4 passed)

- [ ] **Step 5: Checkpoint**

Run: `ruff check procrastinate/middleware.py tests/unit/test_middleware.py && ruff format procrastinate/middleware.py tests/unit/test_middleware.py`
Expected: no errors. (No commit — leave changes in the tree.)

---

## Task 2: `MiddlewareKindMismatch` exception

**Files:**
- Modify: `procrastinate/exceptions.py`
- Test: `tests/unit/test_middleware.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/unit/test_middleware.py`:

```python
from procrastinate import exceptions


def test_middleware_kind_mismatch_is_procrastinate_exception():
    assert issubclass(
        exceptions.MiddlewareKindMismatch, exceptions.ProcrastinateException
    )
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_middleware.py::test_middleware_kind_mismatch_is_procrastinate_exception -v`
Expected: FAIL — `AttributeError: module 'procrastinate.exceptions' has no attribute 'MiddlewareKindMismatch'`

- [ ] **Step 3: Add the exception**

In `procrastinate/exceptions.py`, after the `TaskAlreadyRegistered` class (around line 34-37), add:

```python
class MiddlewareKindMismatch(ProcrastinateException):
    """
    A sync task was given an async middleware (or vice versa). Sync tasks require
    sync middleware; async tasks require async middleware.
    """
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/unit/test_middleware.py::test_middleware_kind_mismatch_is_procrastinate_exception -v`
Expected: PASS

- [ ] **Step 5: Checkpoint**

Run: `ruff check procrastinate/exceptions.py`
Expected: no errors. (No commit.)

---

## Task 3: `Task` stores & validates `task_middleware`

**Files:**
- Modify: `procrastinate/tasks.py` (imports near line 1-12; `Task.__init__` signature near line 76-92; body near line 116-119)
- Test: `tests/unit/test_middleware.py`

- [ ] **Step 1: Write the failing tests**

Append to `tests/unit/test_middleware.py`:

```python
import pytest

from procrastinate import blueprints
from procrastinate.tasks import Task


def _make_task(func, task_middleware=None):
    return Task(
        func,
        blueprint=blueprints.Blueprint(),
        queue="default",
        name="t",
        task_middleware=task_middleware,
    )


def test_task_defaults_to_no_middleware():
    task = _make_task(lambda: None)
    assert task.middlewares == []


def test_task_accepts_matching_sync_middleware():
    def sync_mw(call_next, context, worker):
        return call_next()

    task = _make_task(lambda: None, task_middleware=[sync_mw])
    assert task.middlewares == [sync_mw]


def test_task_rejects_async_middleware_on_sync_task():
    async def async_mw(call_next, context, worker):
        return await call_next()

    with pytest.raises(exceptions.MiddlewareKindMismatch):
        _make_task(lambda: None, task_middleware=[async_mw])


def test_task_rejects_sync_middleware_on_async_task():
    async def my_async_func():
        return None

    def sync_mw(call_next, context, worker):
        return call_next()

    with pytest.raises(exceptions.MiddlewareKindMismatch):
        _make_task(my_async_func, task_middleware=[sync_mw])
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/unit/test_middleware.py -k task_ -v`
Expected: FAIL — `TypeError: __init__() got an unexpected keyword argument 'task_middleware'`

- [ ] **Step 3: Modify `Task`**

In `procrastinate/tasks.py`, add `import inspect` to the imports (top of file, after `import datetime`) and add the middleware import alongside the other `procrastinate` imports:

```python
import datetime
import inspect
import logging
```
```python
from procrastinate import app as app_module
from procrastinate import blueprints, exceptions, jobs, manager, types, utils
from procrastinate import middleware as middleware_module
from procrastinate import retry as retry_module
```

Add the parameter to `Task.__init__` (after `queueing_lock: str | None = None,`):

```python
        queueing_lock: str | None = None,
        task_middleware: list[middleware_module.TaskMiddleware] | None = None,
    ):
```

At the end of `__init__` (after the `self.queueing_lock = queueing_lock` assignment, ~line 119), add:

```python
        #: Middlewares wrapping this task's execution (innermost relative to any
        #: worker-wide middleware). Each must match the task's sync/async nature.
        self.middlewares: list[middleware_module.TaskMiddleware] = task_middleware or []
        task_is_async = inspect.iscoroutinefunction(func)
        for mw in self.middlewares:
            if middleware_module.is_async_middleware(mw) != task_is_async:
                task_kind = "async" if task_is_async else "sync"
                mw_kind = (
                    "async" if middleware_module.is_async_middleware(mw) else "sync"
                )
                mw_name = getattr(mw, "__name__", repr(mw))
                raise exceptions.MiddlewareKindMismatch(
                    f"{mw_kind} middleware {mw_name!r} cannot wrap {task_kind} task "
                    f"{self.name!r}; {task_kind} tasks require {task_kind} middleware."
                )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/unit/test_middleware.py -k task_ -v`
Expected: PASS (4 passed)

- [ ] **Step 5: Run the existing task tests (no regression)**

Run: `pytest tests/unit/test_tasks.py -q`
Expected: PASS

- [ ] **Step 6: Checkpoint**

Run: `ruff check procrastinate/tasks.py`
Expected: no errors. (No commit.)

---

## Task 4: `@app.task(task_middleware=...)` plumbing

**Files:**
- Modify: `procrastinate/blueprints.py` (imports line 10; three `task` overloads at lines 202-302; impl `_wrap` Task() call at lines 321-333)
- Test: `tests/unit/test_middleware.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/unit/test_middleware.py`:

```python
def test_decorator_passes_middleware_to_task():
    bp = blueprints.Blueprint()

    def sync_mw(call_next, context, worker):
        return call_next()

    @bp.task(name="decorated", task_middleware=[sync_mw])
    def decorated():
        return None

    assert bp.tasks["decorated"].middlewares == [sync_mw]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_middleware.py::test_decorator_passes_middleware_to_task -v`
Expected: FAIL — `TypeError: task() got an unexpected keyword argument 'task_middleware'`

- [ ] **Step 3: Add `task_middleware` to `blueprints.task`**

In `procrastinate/blueprints.py`, add the middleware import (line 10, alongside the existing `from procrastinate import exceptions, jobs, periodic, retry, utils`):

```python
from procrastinate import exceptions, jobs, middleware, periodic, retry, utils
```

Add `task_middleware: list[middleware.TaskMiddleware] | None = None,` as the last keyword parameter (after `queueing_lock: str | None = None,`) in **all three** `task` definitions: the two `@overload`s (lines ~214 and ~268) and the implementation (line ~302). For example, the first overload becomes:

```python
        lock: str | None = None,
        queueing_lock: str | None = None,
        task_middleware: list[middleware.TaskMiddleware] | None = None,
    ) -> Callable[[Callable[P, R]], Task[P, R, P]]:
```

In the implementation's docstring (after the `pass_context :` entry, ~line 252), add:

```python
        task_middleware :
            A list of middlewares wrapping this task's execution. Each must match
            the task's nature: sync middleware (a plain function) for a sync task,
            async middleware (a coroutine function) for an async task. See
            `howto/advanced/middleware`.
```

In `_wrap`, pass it into the `Task(...)` constructor (after `pass_context=pass_context,`, ~line 332):

```python
                pass_context=pass_context,
                task_middleware=task_middleware,
            )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/unit/test_middleware.py::test_decorator_passes_middleware_to_task -v`
Expected: PASS

- [ ] **Step 5: Run blueprint tests (no regression)**

Run: `pytest tests/unit/test_blueprints.py -q`
Expected: PASS

- [ ] **Step 6: Checkpoint**

Run: `ruff check procrastinate/blueprints.py`
Expected: no errors. (No commit.)

---

## Task 5: Worker accepts `task_middleware` (plumbing)

**Files:**
- Modify: `procrastinate/app.py` (`WorkerOptions` TypedDict lines 25-38; import; `run_worker_async` docstring ~line 326)
- Modify: `procrastinate/worker.py` (imports line 12-23; `Worker.__init__` signature line 34-50 and body ~line 67)
- Test: `tests/unit/test_middleware.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/unit/test_middleware.py`:

```python
from procrastinate.worker import Worker


def test_worker_stores_task_middleware(not_opened_app):
    def sync_mw(call_next, context, worker):
        return call_next()

    worker = Worker(not_opened_app, task_middleware=[sync_mw])
    assert worker.task_middleware == [sync_mw]


def test_worker_defaults_to_no_task_middleware(not_opened_app):
    worker = Worker(not_opened_app)
    assert worker.task_middleware == []
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/unit/test_middleware.py -k worker_ -v`
Expected: FAIL — `TypeError: __init__() got an unexpected keyword argument 'task_middleware'`

- [ ] **Step 3: Add `task_middleware` to `WorkerOptions` (`app.py`)**

In `procrastinate/app.py`, add the middleware import next to the existing `from procrastinate import (...)` block:

```python
from procrastinate import (
    blueprints,
    exceptions,
    jobs,
    manager,
    middleware,
    schema,
    utils,
)
```

Add the field to `WorkerOptions` (after `stalled_worker_timeout: NotRequired[float]`):

```python
    stalled_worker_timeout: NotRequired[float]
    task_middleware: NotRequired[list[middleware.TaskMiddleware]]
```

In `run_worker_async`'s docstring, after the `stalled_worker_timeout:` entry (~line 326), add:

```python
        task_middleware: ``Optional[list[Middleware]]``
            A list of middlewares wrapping every task this worker runs. Sync
            middlewares apply to sync tasks, async middlewares to async tasks.
            See `howto/advanced/middleware`. (defaults to no middleware)
```

- [ ] **Step 4: Add `task_middleware` to `Worker.__init__` (`worker.py`)**

In `procrastinate/worker.py`, add `middleware` to the `from procrastinate import (...)` block (keep alphabetical: after `jobs,`):

```python
    job_context,
    jobs,
    middleware,
    periodic,
```

Add the parameter to `Worker.__init__` (after `stalled_worker_timeout: float = 30.0,`):

```python
        stalled_worker_timeout: float = 30.0,
        task_middleware: list[middleware.TaskMiddleware] | None = None,
    ):
```

Store it (after `self.stalled_worker_timeout = stalled_worker_timeout`, ~line 67):

```python
        self.stalled_worker_timeout = stalled_worker_timeout
        self.task_middleware: list[middleware.TaskMiddleware] = task_middleware or []
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/unit/test_middleware.py -k worker_ -v`
Expected: PASS (2 passed)

- [ ] **Step 6: Checkpoint**

Run: `ruff check procrastinate/app.py procrastinate/worker.py`
Expected: no errors. (No commit.)

---

## Task 6: Run the middleware chain in the worker

**Files:**
- Modify: `procrastinate/worker.py` (`_process_job` / `ensure_async` at lines 245-267; add `_resolve_task_middlewares` method)
- Test: `tests/unit/test_middleware.py`

- [ ] **Step 1: Write the failing tests**

Append to `tests/unit/test_middleware.py`:

```python
import threading


async def test_sync_middleware_runs_in_the_task_thread(app):
    main_thread = threading.get_ident()
    seen = {}

    def sync_mw(call_next, context, worker):
        seen["mw_thread"] = threading.get_ident()
        return call_next()

    @app.task(name="sync_task")
    def sync_task():
        seen["task_thread"] = threading.get_ident()
        return "ok"

    await sync_task.defer_async()
    await app.run_worker_async(
        wait=False, install_signal_handlers=False, task_middleware=[sync_mw]
    )

    # Middleware and task share one thread, and it's not the event-loop thread.
    assert seen["mw_thread"] == seen["task_thread"]
    assert seen["task_thread"] != main_thread


async def test_async_middleware_wraps_async_task(app):
    order = []

    async def async_mw(call_next, context, worker):
        order.append("before")
        result = await call_next()
        order.append("after")
        return result

    @app.task(name="async_task")
    async def async_task():
        order.append("task")
        return 42

    await async_task.defer_async()
    await app.run_worker_async(
        wait=False, install_signal_handlers=False, task_middleware=[async_mw]
    )

    assert order == ["before", "task", "after"]


async def test_worker_wide_middleware_is_filtered_by_kind(app):
    seen = []

    async def async_mw(call_next, context, worker):
        seen.append("async_mw")
        return await call_next()

    @app.task(name="sync_only")
    def sync_only():
        return None

    await sync_only.defer_async()
    # An async worker-wide middleware must NOT wrap a sync task.
    await app.run_worker_async(
        wait=False, install_signal_handlers=False, task_middleware=[async_mw]
    )

    assert seen == []


async def test_middleware_can_transform_result(app):
    def doubling_mw(call_next, context, worker):
        return call_next() * 2

    @app.task(name="returns_three")
    def returns_three():
        return 3

    job_id = await returns_three.defer_async()
    await app.run_worker_async(
        wait=False, install_signal_handlers=False, task_middleware=[doubling_mw]
    )

    assert app.connector.jobs[job_id]["status"] == "succeeded"


async def test_no_middleware_runs_task_normally(app):
    ran = []

    @app.task(name="plain")
    def plain():
        ran.append(True)

    await plain.defer_async()
    await app.run_worker_async(wait=False, install_signal_handlers=False)

    assert ran == [True]


async def test_middleware_exception_propagates_to_job_status(app):
    def passthrough_mw(call_next, context, worker):
        return call_next()

    @app.task(name="boom")
    def boom():
        raise ValueError("boom")

    job_id = await boom.defer_async()
    await app.run_worker_async(
        wait=False, install_signal_handlers=False, task_middleware=[passthrough_mw]
    )

    # The exception flows through the middleware to the worker's normal handling.
    assert app.connector.jobs[job_id]["status"] == "failed"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/unit/test_middleware.py -k "middleware_runs or async_middleware_wraps or filtered_by_kind or transform_result or no_middleware or exception_propagates" -v`
Expected: FAIL — the worker still runs `task` directly (e.g. `test_sync_middleware_runs_in_the_task_thread` fails with `KeyError: 'mw_thread'`).

- [ ] **Step 3: Add `_resolve_task_middlewares` and rewrite `ensure_async`**

In `procrastinate/worker.py`, add this method to `Worker` (place it just before `_process_job`, ~line 212):

```python
    def _resolve_task_middlewares(
        self, task: tasks.Task, task_is_async: bool
    ) -> list[middleware.TaskMiddleware]:
        # Worker-wide middlewares matching the task's nature (outermost), then the
        # task's own middlewares (innermost, already validated to match).
        worker_wide = [
            mw
            for mw in self.task_middleware
            if middleware.is_async_middleware(mw) == task_is_async
        ]
        return worker_wide + task.middlewares
```

Replace the body of `ensure_async` (lines 245-267 — from `async def ensure_async()` through `return task_result`) with:

```python
            async def ensure_async() -> Any:
                job_args = [context] if task.pass_context else []
                task_is_async = inspect.iscoroutinefunction(task.func)
                middlewares = self._resolve_task_middlewares(task, task_is_async)

                if task_is_async:

                    async def run_async_task():
                        return await task(*job_args, **job.task_kwargs)

                    task_result = await middleware.compose(
                        middlewares, run_async_task, context, self
                    )()
                else:

                    def run_sync_task():
                        return task(*job_args, **job.task_kwargs)

                    task_result = await utils.sync_to_async(
                        middleware.compose(middlewares, run_sync_task, context, self)
                    )

                # In some cases, the task function might be a synchronous function
                # that returns an awaitable without actually being a
                # coroutinefunction. In that case, in the await above, we haven't
                # actually called the task, but merely generated the awaitable that
                # implements the task. In that case, we want to wait this awaitable.
                if inspect.isawaitable(task_result):
                    task_result = await task_result

                return task_result
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/unit/test_middleware.py -k "middleware_runs or async_middleware_wraps or filtered_by_kind or transform_result or no_middleware or exception_propagates" -v`
Expected: PASS (6 passed)

- [ ] **Step 5: Run the full worker suite (no regression)**

Run: `pytest tests/unit/test_worker.py -q`
Expected: PASS

- [ ] **Step 6: Checkpoint**

Run: `ruff check procrastinate/worker.py`
Expected: no errors. (No commit.)

---

## Task 7: Make `worker.stop()` thread-safe

**Files:**
- Modify: `procrastinate/worker.py` (`__init__` ~line 83; `stop()` lines 85-95; `run()` ~line 389)
- Test: `tests/unit/test_middleware.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/unit/test_middleware.py`:

```python
import asyncio


async def test_stop_from_sync_middleware_stops_the_worker(app):
    processed = []

    def stopping_mw(call_next, context, worker):
        processed.append(context.job.id)
        worker.stop()  # called from the task's worker thread
        return call_next()

    @app.task(name="stoppable")
    def stoppable():
        return None

    await stoppable.defer_async()
    await stoppable.defer_async()

    # wait=True means the worker would run forever unless stop() works from the
    # sync middleware's thread; wrap in a timeout so a failure fails (not hangs).
    await asyncio.wait_for(
        app.run_worker_async(
            wait=True, install_signal_handlers=False, task_middleware=[stopping_mw]
        ),
        timeout=5,
    )

    # Concurrency is 1: stop() during the first job prevents the second from running.
    assert len(processed) == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_middleware.py::test_stop_from_sync_middleware_stops_the_worker -v`
Expected: FAIL — the test times out / processes both jobs, because `self._stop_event.set()` from a non-loop thread does not wake the worker loop reliably (`TimeoutError`, or `assert 2 == 1`).

- [ ] **Step 3: Capture the loop and make `stop()` thread-safe**

In `procrastinate/worker.py`, add a loop attribute in `__init__` (after `self.run_task: asyncio.Task[Any] | None = None`, ~line 83):

```python
        self.run_task: asyncio.Task[Any] | None = None
        self._loop: asyncio.AbstractEventLoop | None = None
```

In `run()`, capture the loop next to `self.run_task = asyncio.current_task()` (~line 389):

```python
        self.run_task = asyncio.current_task()
        self._loop = asyncio.get_running_loop()
```

Replace the `stop()` method (lines 85-95) with:

```python
    def stop(self):
        if self._stop_event.is_set():
            return
        self.logger.info(
            "Stop requested",
            extra=self._log_extra(
                context=None, action="stopping_worker", job_result=None
            ),
        )

        try:
            running_loop = asyncio.get_running_loop()
        except RuntimeError:
            running_loop = None

        if self._loop is not None and running_loop is not self._loop:
            # Called from another thread (e.g. a sync task middleware): schedule
            # the event-set on the worker loop so the loop is actually woken.
            self._loop.call_soon_threadsafe(self._stop_event.set)
        else:
            self._stop_event.set()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/unit/test_middleware.py::test_stop_from_sync_middleware_stops_the_worker -v`
Expected: PASS

- [ ] **Step 5: Run the full worker suite (stop() is used widely — no regression)**

Run: `pytest tests/unit/test_worker.py -q`
Expected: PASS

- [ ] **Step 6: Checkpoint**

Run: `pytest tests/unit/test_middleware.py -q`
Expected: PASS (all middleware tests green). (No commit.)

---

## Task 8: Documentation

**Files:**
- Modify: `docs/howto/advanced/middleware.md` (replace whole file)
- Modify: `docs/reference.rst` (Workers/Tasks area)

- [ ] **Step 1: Rewrite `docs/howto/advanced/middleware.md`**

Replace the entire contents with:

````markdown
# Add task middleware

A *task middleware* wraps the execution of a task, letting you run code before and
after it — for logging, OpenTelemetry spans, dependency-injection scopes, resource
cleanup, and so on.

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

# async task -> async middleware
async def span_mw(call_next, context, worker):
    async with tracer.start_as_current_span(context.task.name):
        return await call_next()
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
app.run_worker(task_middleware=[log_mw, span_mw])
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
A future *worker middleware* (running on the event loop, allowing `async with` /
`await` around sync tasks) is planned. Task middleware as described here runs in the
task's own execution context.
:::
````

- [ ] **Step 2: Document the `Middleware` type in `docs/reference.rst`**

In `docs/reference.rst`, after the `Tasks` section's `.. autoclass:: procrastinate.tasks.Task` entry (around line 27-32), add:

```rst
Middleware
----------

.. autofunction:: procrastinate.middleware.compose

.. autofunction:: procrastinate.middleware.is_async_middleware
```

- [ ] **Step 3: Build the docs with warnings-as-errors**

Run: `DJANGO_SETTINGS_MODULE=tests.acceptance.django_settings python -m sphinx -b html -W docs /tmp/docs_build_mw`
Expected: `build succeeded.` (exit 0; no unresolved-reference warnings).

- [ ] **Step 4: Checkpoint**

Run: `ruff check procrastinate tests/unit/test_middleware.py`
Expected: no errors. (No commit.)

---

## Task 9: Full-suite verification

**Files:** none (verification only)

- [ ] **Step 1: Run the whole unit suite**

Run: `pytest tests/unit -q`
Expected: PASS (no regressions; new middleware tests included).

- [ ] **Step 2: Run ruff + format check across changed files**

Run: `ruff check procrastinate tests/unit/test_middleware.py && ruff format --check procrastinate/middleware.py tests/unit/test_middleware.py`
Expected: all checks pass.

- [ ] **Step 3: Type-check (if `basedpyright` available via pre-commit)**

Run: `pre-commit run basedpyright --files procrastinate/middleware.py procrastinate/worker.py procrastinate/tasks.py procrastinate/blueprints.py procrastinate/app.py procrastinate/exceptions.py`
Expected: Passed. (If `basedpyright` is unavailable locally, note it and rely on CI.)

- [ ] **Step 4: Leave everything uncommitted for review**

Run: `git status --short`
Expected: the modified/created files listed, **uncommitted** (per the owner's instruction).

---

## Notes for the implementer

- **`utils.sync_to_async(func, *args, **kwargs)`** runs `func` in a thread with `thread_sensitive=False`. We pass the *composed* zero-arg callable, so the whole sync chain + task run in one thread — this is what makes in-thread middleware (and the future Django connection cleanup) possible. Do **not** wrap each middleware in its own `sync_to_async`.
- The **no-op guarantee**: `compose([], run_task, …)` returns `run_task` unchanged, so with no middleware the worker behaves exactly as before. The `test_no_middleware_runs_task_normally` test guards this.
- `inspect.iscoroutinefunction` already unwraps `functools.partial`; `is_async_middleware` additionally handles callable objects via `__call__`.
- Async-vs-sync **task** detection in the worker uses `inspect.iscoroutinefunction(task.func)` (unchanged from today), so the `Task.__call__`/`run_task` indirection does not affect detection.

### Forward-compat: future worker middleware (NOT in this plan)

Verified that an event-loop `worker_middleware` chain slots in additively later:

- It reuses the same `procrastinate/middleware.py` module, the same generic
  `compose()` (whose `middlewares` param is already typed `Sequence[Callable[..., Any]]`), and a new always-async `WorkerMiddleware` type.
- The **only** change to existing code is one wrapped line at the `ensure_async`
  call site in `_process_job`:
  ```python
  job_result.result = await middleware.compose(
      self.worker_middleware, ensure_async, context, self
  )()
  ```
  With an empty `worker_middleware`, `compose` returns `ensure_async` unchanged, so
  this is behaviorally identical to today. `ensure_async` itself does not change.
- Worker middleware is always-async and applies to every task uniformly (no
  sync/async filtering, no per-task validation, no `_resolve_*`). It nests
  *outside* the task-middleware chain (worker mw → task mw → task), giving
  event-loop-level wrapping even for sync tasks.
- New plumbing only: `worker_middleware` on `run_worker(_async)` / `WorkerOptions` /
  `Worker.__init__`, the `WorkerMiddleware` type, and docs. Nothing in this plan
  needs to be revisited.
