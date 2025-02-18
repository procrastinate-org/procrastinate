from __future__ import annotations

from procrastinate.app import App
from procrastinate.job_context import JobContext
from procrastinate.worker import Worker


async def test_worker_middleware(app: App):
    @app.task()
    async def task_func():
        return 42

    await task_func.defer_async()

    middleware_called = False

    async def custom_worker_middleware(process_task, context, worker):
        assert isinstance(context, JobContext)
        assert isinstance(worker, Worker)
        worker.stop()
        result = await process_task()
        assert result == 42
        nonlocal middleware_called
        middleware_called = True
        return result

    await app.run_worker_async(wait=True, middleware=custom_worker_middleware)

    assert middleware_called


async def test_sync_task_middleware(app: App):
    middleware_called = False

    def sync_task_middleware(process_task, context, worker):
        assert isinstance(context, JobContext)
        assert isinstance(worker, Worker)
        worker.stop()
        result = process_task()
        assert result == 42
        nonlocal middleware_called
        middleware_called = True
        return result

    @app.task(middleware=sync_task_middleware)
    def my_task(a):
        return a

    await my_task.defer_async(a=42)

    await app.run_worker_async(wait=True)

    assert middleware_called


async def test_async_task_middleware(app: App):
    middleware_called = False

    async def async_task_middleware(process_task, context, worker):
        assert isinstance(context, JobContext)
        assert isinstance(worker, Worker)
        worker.stop()
        result = await process_task()
        assert result == 42
        nonlocal middleware_called
        middleware_called = True
        return result

    @app.task(middleware=async_task_middleware)
    async def my_task(a):
        return a

    await my_task.defer_async(a=42)

    await app.run_worker_async(wait=True)

    assert middleware_called
