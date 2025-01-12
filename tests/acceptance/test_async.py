from __future__ import annotations

import asyncio
import time

import pytest

from procrastinate import app as app_module
from procrastinate.contrib import aiopg
from procrastinate.exceptions import JobAborted
from procrastinate.job_context import JobContext
from procrastinate.jobs import Status


@pytest.fixture(params=["psycopg_connector", "aiopg_connector"])
async def async_app(request, psycopg_connector, connection_params):
    app = app_module.App(
        connector={
            "psycopg_connector": psycopg_connector,
            "aiopg_connector": aiopg.AiopgConnector(**connection_params),
        }[request.param]
    )
    async with app.open_async():
        yield app


async def test_defer(async_app: app_module.App):
    sum_results = []
    product_results = []

    @async_app.task(queue="default", name="sum_task")
    def sum_task(a, b):
        sum_results.append(a + b)

    @async_app.task(queue="default", name="product_task")
    async def product_task(a, b):
        product_results.append(a * b)

    await sum_task.defer_async(a=1, b=2)
    await sum_task.configure().defer_async(a=3, b=4)
    await async_app.configure_task(name="sum_task").defer_async(a=5, b=6)
    await product_task.defer_async(a=3, b=4)

    await async_app.run_worker_async(queues=["default"], wait=False)

    assert sum_results == [3, 7, 11]
    assert product_results == [12]


async def test_cancel(async_app: app_module.App):
    sum_results = []

    @async_app.task(queue="default", name="sum_task")
    async def sum_task(a, b):
        sum_results.append(a + b)

    job_id = await sum_task.defer_async(a=1, b=2)
    await sum_task.defer_async(a=3, b=4)

    result = await async_app.job_manager.cancel_job_by_id_async(job_id)
    assert result is True

    status = await async_app.job_manager.get_job_status_async(job_id)
    assert status == Status.CANCELLED

    jobs = list(await async_app.job_manager.list_jobs_async())
    assert len(jobs) == 2

    await async_app.run_worker_async(queues=["default"], wait=False)

    assert sum_results == [7]


async def test_cancel_with_delete(async_app: app_module.App):
    sum_results = []

    @async_app.task(queue="default", name="sum_task")
    async def sum_task(a, b):
        sum_results.append(a + b)

    job_id = await sum_task.defer_async(a=1, b=2)
    await sum_task.defer_async(a=3, b=4)

    result = await async_app.job_manager.cancel_job_by_id_async(job_id, delete_job=True)
    assert result is True

    jobs = list(await async_app.job_manager.list_jobs_async())
    assert len(jobs) == 1

    await async_app.run_worker_async(queues=["default"], wait=False)

    assert sum_results == [7]


async def test_no_job_to_cancel_found(async_app: app_module.App):
    @async_app.task(queue="default", name="example_task")
    def example_task():
        pass

    job_id = await example_task.defer_async()

    result = await async_app.job_manager.cancel_job_by_id_async(job_id + 1)
    assert result is False

    status = await async_app.job_manager.get_job_status_async(job_id)
    assert status == Status.TODO

    jobs = list(await async_app.job_manager.list_jobs_async())
    assert len(jobs) == 1


@pytest.mark.skip_before_version("3.0.0")
@pytest.mark.parametrize("mode", ["listen", "poll"])
async def test_abort_async_task(async_app: app_module.App, mode):
    @async_app.task(queue="default", name="task1")
    async def task1():
        await asyncio.sleep(0.5)

    job_id = await task1.defer_async()

    abort_job_polling_interval = 0.1

    worker_task = asyncio.create_task(
        async_app.run_worker_async(
            queues=["default"],
            wait=False,
            abort_job_polling_interval=abort_job_polling_interval,
            listen_notify=True if mode == "listen" else False,
        )
    )

    await asyncio.sleep(0.05)
    result = await async_app.job_manager.cancel_job_by_id_async(job_id, abort=True)
    assert result is True

    # when listening for notifications, job should cancel within ms
    # if notifications are disabled, job will only cancel after abort_job_polling_interval
    await asyncio.wait_for(
        worker_task, timeout=0.1 if mode == "listen" else abort_job_polling_interval * 2
    )

    status = await async_app.job_manager.get_job_status_async(job_id)
    assert status == Status.ABORTED


@pytest.mark.skip_before_version("3.0.0")
@pytest.mark.parametrize("mode", ["listen", "poll"])
async def test_abort_sync_task(async_app: app_module.App, mode):
    @async_app.task(queue="default", name="task1", pass_context=True)
    def task1(context):
        while True:
            time.sleep(0.02)
            if context.should_abort():
                raise JobAborted

    job_id = await task1.defer_async()

    abort_job_polling_interval = 0.1

    worker_task = asyncio.create_task(
        async_app.run_worker_async(
            queues=["default"],
            wait=False,
            abort_job_polling_interval=abort_job_polling_interval,
            listen_notify=True if mode == "listen" else False,
        )
    )

    await asyncio.sleep(0.05)
    result = await async_app.job_manager.cancel_job_by_id_async(job_id, abort=True)
    assert result is True

    # when listening for notifications, job should cancel within ms
    # if notifications are disabled, job will only cancel after abort_job_polling_interval
    await asyncio.wait_for(
        worker_task, timeout=0.1 if mode == "listen" else abort_job_polling_interval * 2
    )

    status = await async_app.job_manager.get_job_status_async(job_id)
    assert status == Status.ABORTED


async def test_concurrency(async_app: app_module.App):
    results = []

    @async_app.task(queue="default", name="appender")
    async def appender(a: int):
        await asyncio.sleep(0.1)
        results.append(a)

    deferred_tasks = [appender.defer_async(a=i) for i in range(1, 101)]
    for task in deferred_tasks:
        await task

    # with 20 concurrent workers, 100 tasks should take about 100/20 x 0.1  = 0.5s
    # if there is no concurrency, it will take well over 2 seconds and fail

    start_time = time.time()
    try:
        await asyncio.wait_for(
            async_app.run_worker_async(concurrency=20, wait=False), timeout=2
        )
    except asyncio.TimeoutError:
        pytest.fail(
            "Failed to process all jobs within 2 seconds. Is the concurrency respected?"
        )
    duration = time.time() - start_time

    assert (
        duration >= 0.5
    ), "processing jobs faster than expected. Is the concurrency respected?"

    assert len(results) == 100, "Unexpected number of job executions"


@pytest.mark.skip_before_version("3.0.0")
async def test_polling(async_app: app_module.App):
    @async_app.task(queue="default", name="sum")
    async def sum(a: int, b: int):
        return a + b

    # rely on polling to fetch new jobs
    worker_task = asyncio.create_task(
        async_app.run_worker_async(
            concurrency=1,
            wait=True,
            listen_notify=False,
            fetch_job_polling_interval=0.3,
        )
    )

    # long enough for worker to wait until next polling
    await asyncio.sleep(0.1)

    job_id = await sum.defer_async(a=5, b=4)

    await asyncio.sleep(0.1)

    job_status = await async_app.job_manager.get_job_status_async(job_id=job_id)

    assert job_status == Status.TODO, "Job fetched faster than expected."

    await asyncio.sleep(0.2)

    job_status = await async_app.job_manager.get_job_status_async(job_id=job_id)

    assert job_status == Status.SUCCEEDED, "Job should have been fetched and processed."

    try:
        worker_task.cancel()
        await asyncio.wait_for(
            worker_task,
            timeout=0.5,
        )
    except asyncio.CancelledError:
        pass
    except asyncio.TimeoutError:
        pytest.fail("Failed to stop worker")


async def test_retry_when_aborting(async_app: app_module.App):
    attempts = 0

    @async_app.task(queue="default", name="task1", pass_context=True, retry=True)
    async def example_task(context):
        nonlocal attempts
        attempts += 1
        await async_app.job_manager.cancel_job_by_id_async(context.job.id, abort=True)
        raise ValueError()

    job_id = await example_task.defer_async()

    await async_app.run_worker_async(queues=["default"], wait=False)

    status = await async_app.job_manager.get_job_status_async(job_id)
    assert status == Status.FAILED
    assert attempts == 1


async def test_stop_worker(async_app: app_module.App):
    results = []

    @async_app.task(name="appender")
    async def appender(a: int):
        await asyncio.sleep(0.1)
        results.append(a)

    job_ids: list[int] = []

    job_ids.append(await appender.defer_async(a=1))
    job_ids.append(await appender.defer_async(a=2))

    run_task = asyncio.create_task(async_app.run_worker_async(concurrency=2, wait=True))
    await asyncio.sleep(0.5)

    with pytest.raises(asyncio.CancelledError):
        run_task.cancel()
        await asyncio.wait_for(run_task, 1)

    for job_id in job_ids:
        status = await async_app.job_manager.get_job_status_async(job_id)
        assert status == Status.SUCCEEDED


@pytest.mark.skip_before_version("3.0.0")
async def test_stop_worker_aborts_async_jobs_past_shutdown_graceful_timeout(
    async_app: app_module.App,
):
    slow_job_cancelled = False

    @async_app.task(queue="default", name="fast_job")
    async def fast_job():
        pass

    @async_app.task(queue="default", name="slow_job")
    async def slow_job():
        nonlocal slow_job_cancelled
        try:
            await asyncio.sleep(2)
        except asyncio.CancelledError:
            slow_job_cancelled = True
            raise

    fast_job_id = await fast_job.defer_async()
    slow_job_id = await slow_job.defer_async()

    run_task = asyncio.create_task(
        async_app.run_worker_async(wait=False, shutdown_graceful_timeout=0.3)
    )
    await asyncio.sleep(0.05)

    with pytest.raises(asyncio.CancelledError):
        run_task.cancel()
        await run_task

    fast_job_status = await async_app.job_manager.get_job_status_async(fast_job_id)
    slow_job_status = await async_app.job_manager.get_job_status_async(slow_job_id)
    assert fast_job_status == Status.SUCCEEDED
    assert slow_job_status == Status.ABORTED

    assert slow_job_cancelled


@pytest.mark.skip_before_version("3.0.0")
async def test_stop_worker_retries_async_jobs_past_shutdown_graceful_timeout(
    async_app: app_module.App,
):
    slow_job_cancelled = False

    @async_app.task(queue="default", name="slow_job", retry=1)
    async def slow_job():
        nonlocal slow_job_cancelled
        try:
            await asyncio.sleep(2)
        except asyncio.CancelledError:
            slow_job_cancelled = True
            raise

    slow_job_id = await slow_job.defer_async()

    run_task = asyncio.create_task(
        async_app.run_worker_async(wait=False, shutdown_graceful_timeout=0.3)
    )
    await asyncio.sleep(0.05)

    with pytest.raises(asyncio.CancelledError):
        run_task.cancel()
        await run_task

    slow_job_status = await async_app.job_manager.get_job_status_async(slow_job_id)
    assert slow_job_cancelled
    assert slow_job_status == Status.TODO


@pytest.mark.skip_before_version("3.0.0")
async def test_stop_worker_aborts_sync_jobs_past_shutdown_graceful_timeout(
    async_app: app_module.App,
):
    slow_job_cancelled = False

    @async_app.task(queue="default", name="fast_job")
    async def fast_job():
        pass

    @async_app.task(queue="default", name="slow_job", pass_context=True)
    def slow_job(context: JobContext):
        nonlocal slow_job_cancelled
        while True:
            time.sleep(0.05)
            if context.should_abort():
                slow_job_cancelled = True
                raise JobAborted()

    fast_job_id = await fast_job.defer_async()
    slow_job_id = await slow_job.defer_async()

    run_task = asyncio.create_task(
        async_app.run_worker_async(wait=False, shutdown_graceful_timeout=0.3)
    )
    await asyncio.sleep(0.05)

    with pytest.raises(asyncio.CancelledError):
        run_task.cancel()
        await run_task

    fast_job_status = await async_app.job_manager.get_job_status_async(fast_job_id)
    slow_job_status = await async_app.job_manager.get_job_status_async(slow_job_id)
    assert fast_job_status == Status.SUCCEEDED
    assert slow_job_status == Status.ABORTED

    assert slow_job_cancelled


@pytest.mark.skip_before_version("3.0.0")
async def test_stop_worker_retries_sync_jobs_past_shutdown_graceful_timeout(
    async_app: app_module.App,
):
    slow_job_cancelled = False

    @async_app.task(queue="default", name="slow_job", retry=1, pass_context=True)
    def slow_job(context: JobContext):
        nonlocal slow_job_cancelled
        while True:
            time.sleep(0.05)
            if context.should_abort():
                slow_job_cancelled = True
                raise JobAborted()

    slow_job_id = await slow_job.defer_async()

    run_task = asyncio.create_task(
        async_app.run_worker_async(wait=False, shutdown_graceful_timeout=0.3)
    )
    await asyncio.sleep(0.05)

    with pytest.raises(asyncio.CancelledError):
        run_task.cancel()
        await run_task

    slow_job_status = await async_app.job_manager.get_job_status_async(slow_job_id)
    assert slow_job_status == Status.TODO

    assert slow_job_cancelled
