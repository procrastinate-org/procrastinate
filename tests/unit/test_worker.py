from __future__ import annotations

import asyncio
import signal
from typing import cast

import pytest

from procrastinate.app import App
from procrastinate.exceptions import JobAborted
from procrastinate.job_context import JobContext
from procrastinate.jobs import DEFAULT_QUEUE, Job, Status
from procrastinate.testing import InMemoryConnector
from procrastinate.worker import Worker


async def start_worker(worker: Worker):
    task = asyncio.create_task(worker.run())
    await asyncio.sleep(0.01)
    return task


@pytest.fixture
async def worker(app: App, request: pytest.FixtureRequest):
    kwargs = request.param if hasattr(request, "param") else {}
    worker = Worker(app, **kwargs)
    yield worker
    if worker.run_task and not worker.run_task.done():
        worker.stop()
        try:
            await asyncio.wait_for(worker.run_task, timeout=0.2)
        except asyncio.CancelledError:
            pass


@pytest.mark.parametrize(
    "available_jobs, concurrency",
    [
        (0, 1),
        (1, 1),
        (2, 1),
        (1, 2),
        (2, 2),
        (4, 2),
    ],
)
async def test_worker_run_no_wait(app: App, available_jobs, concurrency):
    worker = Worker(app, wait=False, concurrency=concurrency)

    @app.task
    async def perform_job():
        pass

    for i in range(available_jobs):
        await perform_job.defer_async()

    await asyncio.wait_for(worker.run(), 0.1)


async def test_worker_run_wait_until_cancelled(app: App):
    worker = Worker(app, wait=True)
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(worker.run(), 0.05)


async def test_worker_run_wait_stop(app: App, caplog):
    caplog.set_level("INFO")
    worker = Worker(app, wait=True)
    run_task = asyncio.create_task(worker.run())
    # wait just enough to make sure the task is running
    await asyncio.sleep(0.01)
    worker.stop()
    await asyncio.wait_for(run_task, 0.1)

    assert set(caplog.messages) == {
        "Starting worker on all queues",
        "Stop requested",
        "Stopped worker on all queues",
        "No periodic task found, periodic deferrer will not run.",
    }


async def test_worker_run_once_log_messages(app: App, caplog):
    caplog.set_level("INFO")
    worker = Worker(app, wait=False)
    await asyncio.wait_for(worker.run(), 0.1)

    assert set(caplog.messages) == {
        "Starting worker on all queues",
        "No job found. Stopping worker because wait=False",
        "Stopped worker on all queues",
        "No periodic task found, periodic deferrer will not run.",
    }


async def test_worker_run_wait_listen(worker):
    await start_worker(worker)
    connector = cast(InMemoryConnector, worker.app.connector)

    assert connector.notify_event
    assert connector.notify_channels == ["procrastinate_any_queue"]


@pytest.mark.parametrize(
    "available_jobs, worker",
    [
        (2, {"concurrency": 1}),
        (3, {"concurrency": 2}),
    ],
    indirect=["worker"],
)
async def test_worker_run_respects_concurrency(
    worker: Worker, app: App, available_jobs
):
    complete_tasks = asyncio.Event()

    @app.task
    async def perform_job():
        await complete_tasks.wait()

    for _ in range(available_jobs):
        await perform_job.defer_async()

    await start_worker(worker)

    connector = cast(InMemoryConnector, app.connector)

    doings_jobs = list(await connector.list_jobs_all(status=Status.DOING.value))
    todo_jobs = list(await connector.list_jobs_all(status=Status.TODO.value))

    assert len(doings_jobs) == worker.concurrency
    assert len(todo_jobs) == available_jobs - worker.concurrency

    complete_tasks.set()


async def test_worker_run_respects_concurrency_variant(worker: Worker, app: App):
    worker.concurrency = 2

    max_parallelism = 0
    parallel_jobs = 0

    @app.task
    async def perform_job(sleep: float):
        nonlocal max_parallelism
        nonlocal parallel_jobs
        parallel_jobs += 1

        max_parallelism = max(max_parallelism, parallel_jobs)
        await asyncio.sleep(sleep)
        parallel_jobs -= 1

    await perform_job.defer_async(sleep=0.05)
    await perform_job.defer_async(sleep=0.1)

    await start_worker(worker)

    # wait enough to run out of job and to have one pending job
    await asyncio.sleep(0.05)

    assert max_parallelism == 2
    assert parallel_jobs == 1

    # defer more jobs than the worker can process in parallel
    await perform_job.defer_async(sleep=0.05)
    await perform_job.defer_async(sleep=0.05)
    await perform_job.defer_async(sleep=0.05)

    worker._notify_event.set()

    await asyncio.sleep(0.2)
    assert max_parallelism == 2
    assert parallel_jobs == 0


async def test_worker_run_fetches_job_on_notification(worker, app: App):
    complete_tasks = asyncio.Event()

    @app.task
    async def perform_job():
        await complete_tasks.wait()

    await start_worker(worker)

    connector = cast(InMemoryConnector, app.connector)

    assert len([query for query in connector.queries if query[0] == "fetch_job"]) == 1

    await asyncio.sleep(0.01)

    assert len([query for query in connector.queries if query[0] == "fetch_job"]) == 1

    await perform_job.defer_async()
    await asyncio.sleep(0.01)

    assert len([query for query in connector.queries if query[0] == "fetch_job"]) == 2

    complete_tasks.set()


@pytest.mark.parametrize(
    "worker",
    [({"polling_interval": 0.05})],
    indirect=["worker"],
)
async def test_worker_run_respects_polling(worker, app):
    await start_worker(worker)

    connector = cast(InMemoryConnector, app.connector)
    assert len([query for query in connector.queries if query[0] == "fetch_job"]) == 1

    await asyncio.sleep(0.05)

    assert len([query for query in connector.queries if query[0] == "fetch_job"]) == 2


@pytest.mark.parametrize(
    "worker, fail_task",
    [
        ({"delete_jobs": "never"}, False),
        ({"delete_jobs": "never"}, True),
        ({"delete_jobs": "successful"}, True),
    ],
    indirect=["worker"],
)
async def test_process_job_without_deletion(app: App, worker, fail_task):
    @app.task()
    async def task_func():
        if fail_task:
            raise ValueError("Nope")

    job_id = await task_func.defer_async()

    await start_worker(worker)

    connector = cast(InMemoryConnector, app.connector)
    assert job_id in connector.jobs


@pytest.mark.parametrize(
    "worker, fail_task",
    [
        ({"delete_jobs": "successful"}, False),
        ({"delete_jobs": "always"}, False),
        ({"delete_jobs": "always"}, True),
    ],
    indirect=["worker"],
)
async def test_process_job_with_deletion(app: App, worker, fail_task):
    @app.task()
    async def task_func():
        if fail_task:
            raise ValueError("Nope")

    job_id = await task_func.defer_async()

    await start_worker(worker)

    connector = cast(InMemoryConnector, app.connector)
    assert job_id not in connector.jobs


async def test_stopping_worker_waits_for_task(app: App, worker):
    complete_task_event = asyncio.Event()

    @app.task()
    async def task_func():
        await complete_task_event.wait()

    run_task = await start_worker(worker)

    job_id = await task_func.defer_async()

    await asyncio.sleep(0.05)

    # this should still be running waiting for the task to complete
    assert run_task.done() is False

    # tell the task to complete
    complete_task_event.set()

    # this should successfully complete the job and re-raise the CancelledError
    with pytest.raises(asyncio.CancelledError):
        run_task.cancel()
        await asyncio.wait_for(run_task, 0.1)

    status = await app.job_manager.get_job_status_async(job_id)
    assert status == Status.SUCCEEDED


@pytest.mark.parametrize("mode", [("stop"), ("cancel")])
async def test_stopping_worker_aborts_job_after_timeout(app: App, worker, mode):
    complete_task_event = asyncio.Event()
    worker.shutdown_timeout = 0.02

    task_cancelled = False

    @app.task()
    async def task_func():
        nonlocal task_cancelled
        try:
            await complete_task_event.wait()
        except asyncio.CancelledError:
            task_cancelled = True
            raise

    run_task = await start_worker(worker)

    job_id = await task_func.defer_async()

    await asyncio.sleep(0.05)

    # this should still be running waiting for the task to complete
    assert run_task.done() is False

    # we don't tell task to complete, it will be cancelled after timeout

    if mode == "stop":
        worker.stop()

        await asyncio.sleep(0.1)
        assert run_task.done()
        await run_task
    else:
        with pytest.raises(asyncio.CancelledError):
            run_task.cancel()

            await asyncio.sleep(0.1)
            assert run_task.done()
            await run_task

    status = await app.job_manager.get_job_status_async(job_id)
    assert status == Status.ABORTED
    assert task_cancelled


async def test_stopping_worker_job_suppresses_cancellation(app: App, worker):
    complete_task_event = asyncio.Event()
    worker.shutdown_timeout = 0.02

    @app.task()
    async def task_func():
        try:
            await complete_task_event.wait()
        except asyncio.CancelledError:
            # supress the cancellation
            pass

    run_task = await start_worker(worker)

    job_id = await task_func.defer_async()

    await asyncio.sleep(0.05)

    # this should still be running waiting for the task to complete
    assert run_task.done() is False

    worker.stop()

    await asyncio.sleep(0.1)
    assert run_task.done()
    await run_task

    status = await app.job_manager.get_job_status_async(job_id)
    assert status == Status.SUCCEEDED


@pytest.mark.parametrize(
    "worker",
    [({"additional_context": {"foo": "bar"}})],
    indirect=["worker"],
)
async def test_worker_passes_additional_context(app: App, worker):
    @app.task(pass_context=True)
    async def task_func(jobContext: JobContext):
        assert jobContext.additional_context["foo"] == "bar"

    job_id = await task_func.defer_async()

    await start_worker(worker)

    status = await app.job_manager.get_job_status_async(job_id)
    assert status == Status.SUCCEEDED


async def test_run_job_async(app: App, worker):
    result = []

    @app.task(queue="yay", name="task_func")
    async def task_func(a, b):
        result.append(a + b)

    job_id = await task_func.defer_async(a=9, b=3)

    await start_worker(worker)
    assert result == [12]

    status = await app.job_manager.get_job_status_async(job_id)
    assert status == Status.SUCCEEDED


async def test_run_job_sync(app: App, worker):
    result = []

    @app.task(queue="yay", name="task_func")
    def task_func(a, b):
        result.append(a + b)

    job_id = await task_func.defer_async(a=9, b=3)

    await start_worker(worker)
    assert result == [12]

    status = await app.job_manager.get_job_status_async(job_id)
    assert status == Status.SUCCEEDED


async def test_run_job_semi_async(app: App, worker):
    result = []

    @app.task(queue="yay", name="task_func")
    def task_func(a, b):
        async def inner():
            result.append(a + b)

        return inner()

    job_id = await task_func.defer_async(a=9, b=3)

    await start_worker(worker)

    assert result == [12]

    status = await app.job_manager.get_job_status_async(job_id)
    assert status == Status.SUCCEEDED


async def test_run_job_log_result(caplog, app: App, worker):
    caplog.set_level("INFO")

    @app.task(queue="yay", name="task_func")
    async def task_func(a, b):
        return a + b

    await task_func.defer_async(a=9, b=3)

    await start_worker(worker)

    records = [record for record in caplog.records if record.action == "job_success"]
    assert len(records) == 1
    record = records[0]
    assert record.result == 12
    assert "Result: 12" in record.message


async def test_run_task_not_found_status(app: App, worker, caplog):
    job = await app.job_manager.defer_job_async(
        Job(
            task_name="random_task_name",
            queue=DEFAULT_QUEUE,
            lock=None,
            queueing_lock=None,
        )
    )
    assert job.id

    await start_worker(worker)
    await asyncio.sleep(0.01)
    status = await app.job_manager.get_job_status_async(job.id)
    assert status == Status.FAILED

    records = [record for record in caplog.records if record.action == "task_not_found"]
    assert len(records) == 1
    record = records[0]
    assert record.levelname == "ERROR"


class CustomCriticalError(BaseException):
    pass


@pytest.mark.parametrize(
    "critical_error",
    [
        (False),
        (True),
    ],
)
async def test_run_job_error(app: App, worker, critical_error, caplog):
    @app.task(queue="yay", name="task_func")
    def task_func(a, b):
        raise CustomCriticalError("Nope") if critical_error else ValueError("Nope")

    job_id = await task_func.defer_async(a=9, b=3)

    await start_worker(worker)

    await asyncio.sleep(0.05)
    status = await app.job_manager.get_job_status_async(job_id)
    assert status == Status.FAILED

    records = [
        record
        for record in caplog.records
        if hasattr(record, "action") and record.action == "job_error"
    ]
    assert len(records) == 1
    record = records[0]
    assert record.levelname == "ERROR"
    assert "to retry" not in record.message


async def test_run_job_aborted(app: App, worker, caplog):
    caplog.set_level("INFO")

    @app.task(queue="yay", name="task_func")
    async def task_func():
        raise JobAborted()

    job_id = await task_func.defer_async()

    await start_worker(worker)

    status = await app.job_manager.get_job_status_async(job_id)
    assert status == Status.ABORTED

    records = [record for record in caplog.records if record.action == "job_aborted"]
    assert len(records) == 1
    record = records[0]
    assert record.levelname == "INFO"
    assert "Aborted" in record.message


@pytest.mark.parametrize(
    "critical_error, recover_on_attempt_number, expected_status, expected_attempts",
    [
        (False, 2, "succeeded", 2),
        (True, 2, "succeeded", 2),
        (False, 3, "failed", 2),
        (True, 3, "failed", 2),
    ],
)
async def test_run_job_retry_failed_job(
    app: App,
    worker,
    critical_error,
    recover_on_attempt_number,
    expected_status,
    expected_attempts,
):
    worker.wait = False

    attempt = 0

    @app.task(retry=1)
    def task_func():
        nonlocal attempt
        attempt += 1
        if attempt < recover_on_attempt_number:
            raise CustomCriticalError("Nope") if critical_error else ValueError("Nope")

    job_id = await task_func.defer_async()

    await start_worker(worker)

    await asyncio.sleep(0.01)

    connector = cast(InMemoryConnector, app.connector)
    job_row = connector.jobs[job_id]
    assert job_row["status"] == expected_status
    assert job_row["attempts"] == expected_attempts


async def test_run_log_actions(app: App, caplog, worker):
    caplog.set_level("DEBUG")

    done = asyncio.Event()

    @app.task(queue="some_queue")
    def t():
        done.set()

    await t.defer_async()

    await start_worker(worker)

    await asyncio.wait_for(done.wait(), timeout=0.05)

    connector = cast(InMemoryConnector, app.connector)
    assert [q[0] for q in connector.queries] == [
        "defer_job",
        "fetch_job",
        "finish_job",
        "fetch_job",
    ]

    logs = {(r.action, r.levelname) for r in caplog.records}
    # remove the periodic_deferrer_no_task log record because that makes the test flaky
    assert {
        ("about_to_defer_job", "DEBUG"),
        ("job_defer", "INFO"),
        ("start_worker", "INFO"),
        ("loaded_job_info", "DEBUG"),
        ("start_job", "INFO"),
        ("job_success", "INFO"),
        ("finish_task", "DEBUG"),
    } <= logs


async def test_run_log_current_job_when_stopping(app: App, worker, caplog):
    caplog.set_level("DEBUG")
    complete_job_event = asyncio.Event()

    @app.task(queue="some_queue")
    async def t():
        await complete_job_event.wait()

    job_id = await t.defer_async()
    run_task = await start_worker(worker)
    worker.stop()
    await asyncio.sleep(0.01)
    complete_job_event.set()

    await asyncio.wait_for(run_task, timeout=0.05)
    # We want to make sure that the log that names the current running task fired.
    logs = " ".join(r.message for r in caplog.records)
    assert "Stop requested" in logs
    assert (
        f"Waiting for job to finish: worker: tests.unit.test_worker.t[{job_id}]()"
        in logs
    )


async def test_run_no_listen_notify(app: App, worker):
    worker.listen_notify = False
    await start_worker(worker)
    connector = cast(InMemoryConnector, app.connector)
    assert connector.notify_event is None


async def test_run_no_signal_handlers(worker, kill_own_pid):
    worker.install_signal_handlers = False
    await start_worker(worker)
    with pytest.raises(KeyboardInterrupt):
        await asyncio.sleep(0.01)
        # Test that handlers are NOT installed
        kill_own_pid(signal=signal.SIGINT)
