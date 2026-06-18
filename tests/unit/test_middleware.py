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


def test_task_defaults_to_no_task_middleware():
    task = _make_task(lambda: None)
    assert task.task_middleware == []


def test_task_accepts_matching_sync_middleware():
    def sync_mw(call_next, context, worker):
        return call_next()

    task = _make_task(lambda: None, task_middleware=[sync_mw])
    assert task.task_middleware == [sync_mw]


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


def test_task_rejects_non_callable_task_middleware():
    with pytest.raises(TypeError, match="not callable"):
        _make_task(lambda: None, task_middleware=["oops"])  # type: ignore[list-item]


def test_worker_rejects_non_callable_task_middleware(not_opened_app):
    with pytest.raises(TypeError, match="not callable"):
        Worker(not_opened_app, task_middleware=["oops"])  # type: ignore[list-item]


def test_decorator_passes_middleware_to_task():
    bp = blueprints.Blueprint()

    def sync_mw(call_next, context, worker):
        return call_next()

    @bp.task(name="decorated", task_middleware=[sync_mw])
    def decorated():
        return None

    assert bp.tasks["decorated"].task_middleware == [sync_mw]


def test_worker_stores_task_middleware(not_opened_app):
    def sync_mw(call_next, context, worker):
        return call_next()

    worker = Worker(not_opened_app, task_middleware=[sync_mw])
    assert worker.task_middleware == [sync_mw]


def test_worker_defaults_to_no_task_middleware(not_opened_app):
    worker = Worker(not_opened_app)
    assert worker.task_middleware == []


def test_worker_defaults_to_no_worker_middleware(not_opened_app):
    worker = Worker(not_opened_app)
    assert worker.worker_middleware == []


def test_worker_stores_worker_middleware(not_opened_app):
    async def mw(call_next, context, worker):
        return await call_next()

    worker = Worker(not_opened_app, worker_middleware=[mw])
    assert worker.worker_middleware == [mw]


def test_worker_rejects_non_callable_worker_middleware(not_opened_app):
    with pytest.raises(TypeError, match="not callable"):
        Worker(not_opened_app, worker_middleware=["oops"])  # type: ignore[list-item]


def test_worker_rejects_sync_worker_middleware(not_opened_app):
    def sync_mw(call_next, context, worker):
        return call_next()

    with pytest.raises(TypeError, match="must be async"):
        Worker(not_opened_app, worker_middleware=[sync_mw])  # type: ignore[list-item]


async def test_sync_task_middleware_runs_in_the_task_thread(app):
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


async def test_async_task_middleware_wraps_async_task(app):
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


async def test_per_task_async_middleware_wraps_async_task(app):
    order = []

    async def async_mw(call_next, context, worker):
        order.append("before")
        result = await call_next()
        order.append("after")
        return result

    @app.task(name="async_task", task_middleware=[async_mw])
    async def async_task():
        order.append("task")

    await async_task.defer_async()
    await app.run_worker_async(wait=False, install_signal_handlers=False)

    assert order == ["before", "task", "after"]


async def test_worker_wide_task_middleware_is_filtered_by_kind(app):
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


async def test_mixed_kind_worker_wide_task_middlewares_wrap_matching_tasks(app):
    # The documented way to cover both task kinds worker-wide: one middleware
    # of each kind; each task gets exactly the matching one.
    seen = []

    def sync_mw(call_next, context, worker):
        seen.append(f"sync_mw:{context.task.name}")
        return call_next()

    async def async_mw(call_next, context, worker):
        seen.append(f"async_mw:{context.task.name}")
        return await call_next()

    @app.task(name="sync_task")
    def sync_task():
        return None

    @app.task(name="async_task")
    async def async_task():
        return None

    await sync_task.defer_async()
    await async_task.defer_async()
    await app.run_worker_async(
        wait=False, install_signal_handlers=False, task_middleware=[sync_mw, async_mw]
    )

    assert sorted(seen) == ["async_mw:async_task", "sync_mw:sync_task"]


async def test_worker_wide_task_middleware_wraps_outside_per_task_middleware(app):
    order = []

    def make_mw(label):
        def mw(call_next, context, worker):
            order.append(f"before:{label}")
            result = call_next()
            order.append(f"after:{label}")
            return result

        return mw

    @app.task(name="ordered", task_middleware=[make_mw("per_task")])
    def ordered():
        order.append("task")

    await ordered.defer_async()
    await app.run_worker_async(
        wait=False,
        install_signal_handlers=False,
        task_middleware=[make_mw("worker_wide")],
    )

    assert order == [
        "before:worker_wide",
        "before:per_task",
        "task",
        "after:per_task",
        "after:worker_wide",
    ]


async def test_task_middleware_can_transform_result(app):
    seen = []

    def doubling_mw(call_next, context, worker):
        return call_next() * 2

    def recording_mw(call_next, context, worker):
        result = call_next()
        seen.append(result)
        return result

    @app.task(name="returns_three", task_middleware=[doubling_mw])
    def returns_three():
        return 3

    job_id = await returns_three.defer_async()
    await app.run_worker_async(
        wait=False, install_signal_handlers=False, task_middleware=[recording_mw]
    )

    # The worker-wide middleware observes the per-task middleware's transformation.
    assert seen == [6]
    assert app.connector.jobs[job_id]["status"] == "succeeded"


async def test_no_task_middleware_runs_task_normally(app):
    ran = []

    @app.task(name="plain")
    def plain():
        ran.append(True)

    await plain.defer_async()
    await app.run_worker_async(wait=False, install_signal_handlers=False)

    assert ran == [True]


async def test_task_middleware_exception_propagates_to_job_status(app):
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


async def test_job_aborted_propagates_through_task_middleware(app):
    def passthrough_mw(call_next, context, worker):
        return call_next()

    @app.task(name="aborting")
    def aborting():
        raise exceptions.JobAborted

    job_id = await aborting.defer_async()
    await app.run_worker_async(
        wait=False, install_signal_handlers=False, task_middleware=[passthrough_mw]
    )

    # JobAborted must reach the worker's status classification unchanged: the
    # job ends aborted, not failed.
    assert app.connector.jobs[job_id]["status"] == "aborted"


async def test_retry_works_through_task_middleware(app):
    mw_calls = []

    def counting_mw(call_next, context, worker):
        mw_calls.append(context.job.id)
        return call_next()

    @app.task(name="flaky", retry=1)
    def flaky():
        raise ValueError("nope")

    job_id = await flaky.defer_async()
    await app.run_worker_async(
        wait=False, install_signal_handlers=False, task_middleware=[counting_mw]
    )

    # The retry strategy still sees the task's exception through the middleware;
    # both attempts run, each wrapped by the middleware.
    assert app.connector.jobs[job_id]["status"] == "failed"
    assert app.connector.jobs[job_id]["attempts"] == 2
    assert mw_calls == [job_id, job_id]


async def test_stop_from_sync_task_middleware_stops_the_worker(app):
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


async def test_worker_middleware_wraps_async_task(app):
    order = []

    async def mw(call_next, context, worker):
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
        wait=False, install_signal_handlers=False, worker_middleware=[mw]
    )

    assert order == ["before", "task", "after"]


async def test_worker_middleware_wraps_sync_task(app):
    # Headline capability: an always-async middleware wraps a SYNC task — an async
    # task middleware cannot do this.
    order = []

    async def mw(call_next, context, worker):
        order.append("before")
        result = await call_next()
        order.append("after")
        return result

    @app.task(name="sync_task")
    def sync_task():
        order.append("task")
        return "ok"

    await sync_task.defer_async()
    await app.run_worker_async(
        wait=False, install_signal_handlers=False, worker_middleware=[mw]
    )

    assert order == ["before", "task", "after"]


async def test_worker_middleware_wraps_outside_task_middleware(app):
    order = []

    async def worker_mw(call_next, context, worker):
        order.append("before:worker_mw")
        result = await call_next()
        order.append("after:worker_mw")
        return result

    async def per_task_mw(call_next, context, worker):
        order.append("before:per_task")
        result = await call_next()
        order.append("after:per_task")
        return result

    @app.task(name="ordered", task_middleware=[per_task_mw])
    async def ordered():
        order.append("task")

    await ordered.defer_async()
    await app.run_worker_async(
        wait=False, install_signal_handlers=False, worker_middleware=[worker_mw]
    )

    assert order == [
        "before:worker_mw",
        "before:per_task",
        "task",
        "after:per_task",
        "after:worker_mw",
    ]


async def test_worker_middleware_can_transform_result(app):
    seen = []

    async def doubling_mw(call_next, context, worker):
        return await call_next() * 2

    async def recording_mw(call_next, context, worker):
        result = await call_next()
        seen.append(result)
        return result

    @app.task(name="returns_three")
    async def returns_three():
        return 3

    job_id = await returns_three.defer_async()
    # recording_mw is outermost, so it observes doubling_mw's transformation.
    await app.run_worker_async(
        wait=False,
        install_signal_handlers=False,
        worker_middleware=[recording_mw, doubling_mw],
    )

    assert seen == [6]
    assert app.connector.jobs[job_id]["status"] == "succeeded"


async def test_no_worker_middleware_runs_task_normally(app):
    ran = []

    @app.task(name="plain")
    async def plain():
        ran.append(True)

    await plain.defer_async()
    await app.run_worker_async(wait=False, install_signal_handlers=False)

    assert ran == [True]


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


async def test_worker_middleware_exception_propagates_to_job_status(app):
    async def passthrough_mw(call_next, context, worker):
        return await call_next()

    @app.task(name="boom")
    async def boom():
        raise ValueError("boom")

    job_id = await boom.defer_async()
    await app.run_worker_async(
        wait=False, install_signal_handlers=False, worker_middleware=[passthrough_mw]
    )

    assert app.connector.jobs[job_id]["status"] == "failed"


async def test_job_aborted_propagates_through_worker_middleware(app):
    async def passthrough_mw(call_next, context, worker):
        return await call_next()

    @app.task(name="aborting")
    async def aborting():
        raise exceptions.JobAborted

    job_id = await aborting.defer_async()
    await app.run_worker_async(
        wait=False, install_signal_handlers=False, worker_middleware=[passthrough_mw]
    )

    assert app.connector.jobs[job_id]["status"] == "aborted"


async def test_retry_works_through_worker_middleware(app):
    mw_calls = []

    async def counting_mw(call_next, context, worker):
        mw_calls.append(context.job.id)
        return await call_next()

    @app.task(name="flaky", retry=1)
    async def flaky():
        raise ValueError("nope")

    job_id = await flaky.defer_async()
    await app.run_worker_async(
        wait=False, install_signal_handlers=False, worker_middleware=[counting_mw]
    )

    assert app.connector.jobs[job_id]["status"] == "failed"
    assert app.connector.jobs[job_id]["attempts"] == 2
    assert mw_calls == [job_id, job_id]


async def test_stop_from_worker_middleware_stops_the_worker(app):
    processed = []

    async def stopping_mw(call_next, context, worker):
        processed.append(context.job.id)
        worker.stop()
        return await call_next()

    @app.task(name="stoppable")
    async def stoppable():
        return None

    await stoppable.defer_async()
    await stoppable.defer_async()

    # wait=True would run forever unless stop() works; timeout so a failure fails
    # rather than hangs.
    await asyncio.wait_for(
        app.run_worker_async(
            wait=True, install_signal_handlers=False, worker_middleware=[stopping_mw]
        ),
        timeout=5,
    )

    # Concurrency is 1: stop() during the first job prevents the second from running.
    assert len(processed) == 1


async def test_worker_middleware_from_worker_defaults_is_applied():
    # Configured on worker_defaults (NOT passed to run_worker), so it must reach the
    # worker via the {**worker_defaults, **kwargs} merge — the Django-contrib path.
    seen = []

    async def record_mw(call_next, context, worker):
        seen.append(context.task.name)
        return await call_next()

    app = App(
        connector=testing.InMemoryConnector(),
        worker_defaults={"worker_middleware": [record_mw]},
    )
    async with app.open_async():

        @app.task(name="wd_task")
        async def wd_task():
            return None

        await wd_task.defer_async()
        await app.run_worker_async(wait=False, install_signal_handlers=False)

    assert seen == ["wd_task"]
