from __future__ import annotations

import asyncio
import functools
import threading

import pytest

from procrastinate import App, blueprints, exceptions, middleware, testing
from procrastinate.tasks import Task
from procrastinate.worker import Worker


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


def test_is_async_middleware_handles_partial_of_async_callable():
    class AsyncCallable:
        async def __call__(self, call_next, context, worker): ...

    assert middleware.is_async_middleware(functools.partial(AsyncCallable())) is True


def test_middleware_kind_mismatch_is_procrastinate_exception():
    assert issubclass(
        exceptions.MiddlewareKindMismatch, exceptions.ProcrastinateException
    )


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


def test_decorator_passes_middleware_to_task():
    bp = blueprints.Blueprint()

    def sync_mw(call_next, context, worker):
        return call_next()

    @bp.task(name="decorated", task_middleware=[sync_mw])
    def decorated():
        return None

    assert bp.tasks["decorated"].middlewares == [sync_mw]


def test_worker_stores_task_middleware(not_opened_app):
    def sync_mw(call_next, context, worker):
        return call_next()

    worker = Worker(not_opened_app, task_middleware=[sync_mw])
    assert worker.task_middleware == [sync_mw]


def test_worker_defaults_to_no_task_middleware(not_opened_app):
    worker = Worker(not_opened_app)
    assert worker.task_middleware == []


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


async def test_task_middleware_from_worker_defaults_is_applied():
    # The middleware is configured on the App's worker_defaults (NOT passed to
    # run_worker), so it must reach the worker via the {**worker_defaults,
    # **kwargs} merge in App._worker. This is the path the Django contrib uses.
    seen = []

    def record_mw(call_next, context, worker):
        seen.append(context.task.name)
        return call_next()

    app = App(
        connector=testing.InMemoryConnector(),
        worker_defaults={"task_middleware": [record_mw]},
    )
    async with app.open_async():

        @app.task(name="wd_task")
        def wd_task():
            return None

        await wd_task.defer_async()
        await app.run_worker_async(wait=False, install_signal_handlers=False)

    assert seen == ["wd_task"]
