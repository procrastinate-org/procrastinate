from __future__ import annotations

import asyncio
import contextlib
import datetime
import signal
from collections.abc import Callable
from typing import cast
from unittest import mock

import pytest
from pytest_mock import MockerFixture

from procrastinate import utils
from procrastinate.app import App
from procrastinate.exceptions import JobAborted
from procrastinate.job_context import JobContext
from procrastinate.jobs import DEFAULT_QUEUE, Job, Status
from procrastinate.testing import InMemoryConnector
from procrastinate.worker import Worker


async def start_worker(worker: Worker):
    task = asyncio.create_task(worker.run())
    # Yield once so the task gets scheduled, but grant it no wall-clock budget:
    # callers must synchronise on an observable state, never on elapsed time.
    await asyncio.sleep(0)
    return task


async def wait_for(condition: Callable[[], bool], timeout: float = 2):
    async def poll():
        while not condition():
            await asyncio.sleep(0.001)

    await asyncio.wait_for(poll(), timeout)


async def wait_for_job_status(
    app: App, job_id: int, status: Status, timeout: float = 2
):
    """
    Wait until the job reaches `status`, then assert it did. On timeout, the
    assertion reports the status the job is actually stuck in.
    """
    actual = None

    async def poll():
        nonlocal actual
        while (actual := await app.job_manager.get_job_status_async(job_id)) != status:
            await asyncio.sleep(0.001)

    with contextlib.suppress(TimeoutError):
        await asyncio.wait_for(poll(), timeout)

    assert actual == status


def count_queries(app: App, query_name: str) -> int:
    connector = cast(InMemoryConnector, app.connector)
    return len([query for query in connector.queries if query[0] == query_name])


@pytest.fixture
async def worker(app: App, request: pytest.FixtureRequest):
    kwargs = request.param if hasattr(request, "param") else {}
    worker = Worker(app, **kwargs)
    yield worker
    if worker.run_task and not worker.run_task.done():
        worker.stop()
        try:
            await asyncio.wait_for(worker.run_task, timeout=5)
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

    await asyncio.wait_for(worker.run(), 2)


async def test_worker_run_wait_until_cancelled(app: App):
    worker = Worker(app, wait=True)
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(worker.run(), 0.05)


async def test_worker_run_wait_stop(app: App, caplog):
    caplog.set_level("INFO")
    worker = Worker(app, wait=True)
    run_task = asyncio.create_task(worker.run())
    await wait_for(lambda: "Starting worker on all queues" in caplog.messages)
    worker.stop()
    await asyncio.wait_for(run_task, 2)

    assert set(caplog.messages) == {
        "Starting worker on all queues",
        "Stop requested",
        "Stopped worker on all queues",
        "No periodic task found, periodic deferrer will not run.",
    }


async def test_stop_requested_before_run_loop_starts_is_not_lost(app: App):
    worker = Worker(app, wait=True, install_signal_handlers=False)

    original_run_loop = worker._run_loop

    async def run_loop_with_late_start():
        # Simulate a stop() landing after run() scheduled the run loop task but
        # before the task's first statement; if it gets erased, with wait=True
        # the worker runs forever.
        worker.stop()
        await original_run_loop()

    worker._run_loop = run_loop_with_late_start

    await asyncio.wait_for(worker.run(), timeout=2)


def test_stop_after_run_exited_with_error_does_not_raise(not_opened_app: App):
    # If run() dies on an exception (e.g. a database error), the stop event is
    # never set and the worker's event loop ends up closed. A late stop() (e.g.
    # from a signal handler or another thread) must not try to wake that loop.
    worker = Worker(not_opened_app, wait=True, install_signal_handlers=False)

    async def run_until_error():
        async with not_opened_app.open_async():
            failing_fetch = mock.Mock(side_effect=ConnectionError("db down"))
            worker._fetch_and_process_jobs = failing_fetch
            await worker.run()

    with pytest.raises(ConnectionError):
        asyncio.run(run_until_error())

    worker.stop()


async def test_worker_run_once_log_messages(app: App, caplog):
    caplog.set_level("INFO")
    worker = Worker(app, wait=False)
    await asyncio.wait_for(worker.run(), 2)

    assert set(caplog.messages) == {
        "Starting worker on all queues",
        "No job found. Stopping worker because wait=False",
        "Stopped worker on all queues",
        "No periodic task found, periodic deferrer will not run.",
    }


async def test_worker_run_wait_listen(worker):
    connector = cast(InMemoryConnector, worker.app.connector)

    await start_worker(worker)
    await wait_for(lambda: bool(connector.notify_channels))

    assert connector.notify_channels == ["procrastinate_any_queue_v1"]


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
    started_jobs = 0

    @app.task
    async def perform_job():
        nonlocal started_jobs
        started_jobs += 1
        await complete_tasks.wait()

    for _ in range(available_jobs):
        await perform_job.defer_async()

    await start_worker(worker)
    await wait_for(lambda: started_jobs >= worker.concurrency)

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
    started_jobs = 0
    # Each job holds its slot until the test opens its gate. Sleeping instead
    # would make the assertions depend on jobs finishing in the window between
    # two sleeps, which doesn't hold on a loaded CI runner.
    gates = [asyncio.Event() for _ in range(5)]

    @app.task
    async def perform_job(index: int):
        nonlocal max_parallelism
        nonlocal parallel_jobs
        nonlocal started_jobs
        parallel_jobs += 1
        started_jobs += 1

        max_parallelism = max(max_parallelism, parallel_jobs)
        await gates[index].wait()
        parallel_jobs -= 1

    await perform_job.defer_async(index=0)
    await perform_job.defer_async(index=1)

    await start_worker(worker)

    # Both jobs fit within the concurrency budget, so both are running.
    await wait_for(lambda: started_jobs >= 2)
    assert max_parallelism == 2
    assert parallel_jobs == 2

    # Let the first job finish; the second one keeps holding its slot.
    gates[0].set()
    await wait_for(lambda: parallel_jobs <= 1)
    assert parallel_jobs == 1

    # defer more jobs than the worker can process in parallel: only one of them
    # can start, in the slot job 0 just freed.
    for index in (2, 3, 4):
        await perform_job.defer_async(index=index)

    await wait_for(lambda: started_jobs >= 3)
    assert parallel_jobs == 2
    assert max_parallelism == 2

    for gate in gates:
        gate.set()

    await wait_for(lambda: started_jobs >= 5 and parallel_jobs == 0)
    assert max_parallelism == 2


async def test_worker_run_fetches_job_on_notification(worker, app: App):
    complete_tasks = asyncio.Event()

    @app.task
    async def perform_job():
        await complete_tasks.wait()

    await start_worker(worker)

    await wait_for(lambda: count_queries(app, "fetch_job") >= 1)
    assert count_queries(app, "fetch_job") == 1

    # Nothing was deferred, so the worker stays idle instead of fetching again.
    await asyncio.sleep(0.01)
    assert count_queries(app, "fetch_job") == 1

    await perform_job.defer_async()

    await wait_for(lambda: count_queries(app, "fetch_job") >= 2)
    assert count_queries(app, "fetch_job") == 2

    complete_tasks.set()


@pytest.mark.parametrize(
    "worker",
    [({"fetch_job_polling_interval": 0.2})],
    indirect=["worker"],
)
async def test_worker_run_respects_polling(worker, app):
    await start_worker(worker)

    await wait_for(lambda: count_queries(app, "fetch_job") >= 1)
    assert count_queries(app, "fetch_job") == 1

    await wait_for(lambda: count_queries(app, "fetch_job") >= 2)
    assert count_queries(app, "fetch_job") == 2


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
    await wait_for(lambda: count_queries(app, "finish_job") >= 1)

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
    await wait_for(lambda: count_queries(app, "finish_job") >= 1)

    connector = cast(InMemoryConnector, app.connector)
    assert job_id not in connector.jobs


async def test_stopping_worker_waits_for_task(app: App, worker):
    job_started_event = asyncio.Event()
    complete_task_event = asyncio.Event()

    @app.task()
    async def task_func():
        job_started_event.set()
        await complete_task_event.wait()

    run_task = await start_worker(worker)

    job_id = await task_func.defer_async()

    await wait_for(job_started_event.is_set)

    # this should still be running waiting for the task to complete
    assert run_task.done() is False

    # tell the task to complete
    complete_task_event.set()

    # this should successfully complete the job and re-raise the CancelledError
    run_task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await asyncio.wait_for(run_task, 2)

    status = await app.job_manager.get_job_status_async(job_id)
    assert status == Status.SUCCEEDED


@pytest.mark.parametrize("mode", [("stop"), ("cancel")])
async def test_stopping_worker_aborts_job_after_timeout(app: App, worker, mode):
    job_started_event = asyncio.Event()
    complete_task_event = asyncio.Event()
    worker.shutdown_graceful_timeout = 0.02

    task_cancelled = False

    @app.task()
    async def task_func():
        nonlocal task_cancelled
        job_started_event.set()
        try:
            await complete_task_event.wait()
        except asyncio.CancelledError:
            task_cancelled = True
            raise

    run_task = await start_worker(worker)

    job_id = await task_func.defer_async()

    await wait_for(job_started_event.is_set)

    # this should still be running waiting for the task to complete
    assert run_task.done() is False

    # we don't tell task to complete, it will be cancelled after timeout

    if mode == "stop":
        worker.stop()

        await asyncio.wait_for(run_task, 2)
    else:
        run_task.cancel()

        with pytest.raises(asyncio.CancelledError):
            await asyncio.wait_for(run_task, 2)

    status = await app.job_manager.get_job_status_async(job_id)
    assert status == Status.ABORTED
    assert task_cancelled


async def test_stopping_worker_job_suppresses_cancellation(app: App, worker):
    job_started_event = asyncio.Event()
    complete_task_event = asyncio.Event()
    worker.shutdown_graceful_timeout = 0.02

    @app.task()
    async def task_func():
        job_started_event.set()
        try:
            await complete_task_event.wait()
        except asyncio.CancelledError:
            # supress the cancellation
            pass

    run_task = await start_worker(worker)

    job_id = await task_func.defer_async()

    await wait_for(job_started_event.is_set)

    # this should still be running waiting for the task to complete
    assert run_task.done() is False

    worker.stop()

    await asyncio.wait_for(run_task, 2)

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

    await wait_for_job_status(app, job_id, Status.SUCCEEDED)


async def test_run_job_async(app: App, worker):
    result = []

    @app.task(queue="yay", name="task_func")
    async def task_func(a, b):
        result.append(a + b)

    job_id = await task_func.defer_async(a=9, b=3)

    await start_worker(worker)

    await wait_for_job_status(app, job_id, Status.SUCCEEDED)
    assert result == [12]


async def test_run_job_sync(app: App, worker):
    result = []

    @app.task(queue="yay", name="task_func")
    def task_func(a, b):
        result.append(a + b)

    job_id = await task_func.defer_async(a=9, b=3)

    await start_worker(worker)

    await wait_for_job_status(app, job_id, Status.SUCCEEDED)
    assert result == [12]


async def test_run_job_semi_async(app: App, worker):
    result = []

    @app.task(queue="yay", name="task_func")
    def task_func(a, b):
        async def inner():
            result.append(a + b)

        return inner()

    job_id = await task_func.defer_async(a=9, b=3)

    await start_worker(worker)

    await wait_for_job_status(app, job_id, Status.SUCCEEDED)
    assert result == [12]


async def test_run_job_log_result(caplog, app: App, worker):
    caplog.set_level("INFO")

    @app.task(queue="yay", name="task_func")
    async def task_func(a, b):
        return a + b

    job_id = await task_func.defer_async(a=9, b=3)

    await start_worker(worker)

    await wait_for_job_status(app, job_id, Status.SUCCEEDED)

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

    await wait_for_job_status(app, job.id, Status.FAILED)

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

    await wait_for_job_status(app, job_id, Status.FAILED)

    records = [
        record
        for record in caplog.records
        if hasattr(record, "action") and record.action == "job_error"
    ]
    assert len(records) == 1
    record = records[0]
    assert record.levelname == "ERROR"
    assert "to retry" not in record.message


async def test_run_job_raising_job_aborted(app: App, worker, caplog):
    caplog.set_level("INFO")

    @app.task(queue="yay", name="task_func")
    async def task_func():
        raise JobAborted()

    job_id = await task_func.defer_async()

    await start_worker(worker)

    await wait_for_job_status(app, job_id, Status.ABORTED)

    records = [record for record in caplog.records if record.action == "job_aborted"]
    assert len(records) == 1
    record = records[0]
    assert record.levelname == "INFO"
    assert "Aborted" in record.message


async def test_abort_async_job(app: App, worker):
    job_started_event = asyncio.Event()
    # Never set: the job only ever ends by being cancelled.
    never = asyncio.Event()

    @app.task(queue="yay", name="task_func")
    async def task_func():
        job_started_event.set()
        await never.wait()

    job_id = await task_func.defer_async()

    await start_worker(worker)
    # Aborting a job that is not running yet cancels it instead.
    await wait_for(job_started_event.is_set)

    await app.job_manager.cancel_job_by_id_async(job_id, abort=True)

    await wait_for_job_status(app, job_id, Status.ABORTED)


async def test_abort_async_job_during_graceful_shutdown(app: App, caplog):
    """
    Tests that a running job can be successfully aborted after the worker that is running
    it has received a graceful shutdown request.
    """
    caplog.set_level("INFO")

    async def wait_for_msg(msg):
        """Poll until specified status is seen in log."""
        while True:
            for record in caplog.records:
                if msg in record.msg:
                    return
            await asyncio.sleep(0.01)

    async def wait_for_status(job_manager, job_id, status):
        """Poll until specified job status is seen."""
        while True:
            if status == await job_manager.get_job_status_async(job_id):
                return
            await asyncio.sleep(0.01)

    @app.task()
    async def task_func():
        await asyncio.Event().wait()

    # Defer the task, start a worker to process it, and wait for the job have
    # DOING status.
    job_id = await task_func.defer_async()
    worker = Worker(
        app,
        abort_job_polling_interval=0.01,
        fetch_job_polling_interval=0.01,
        # Disable listen_notify to test abort polling.
        listen_notify=False,
        shutdown_graceful_timeout=None,
    )
    run_task = await start_worker(worker)
    await asyncio.wait_for(wait_for_status(app.job_manager, job_id, Status.DOING), 1)

    # Ask the worker to shutdown, verify it has begun to shut down, and verify
    # the job still has DOING status.
    worker.stop()
    await asyncio.wait_for(wait_for_msg("Waiting for job to finish"), 1)
    assert await app.job_manager.get_job_status_async(job_id) == Status.DOING

    # Abort the job and verify the abortion was successful.
    await app.job_manager.cancel_job_by_id_async(job_id, abort=True)
    await asyncio.wait_for(wait_for_status(app.job_manager, job_id, Status.ABORTED), 1)

    await run_task


async def test_abort_async_job_while_finishing(app: App, worker, mocker: MockerFixture):
    """
    Tests that aborting a job after that job completes but before the job status is updated
    does not prevent the job status from being updated
    """
    connector = cast(InMemoryConnector, app.connector)
    original_finish_job_run = connector.finish_job_run

    finish_job_started_event = asyncio.Event()
    complete_finish_job_event = asyncio.Event()

    async def delayed_finish_job_run(**arguments):
        finish_job_started_event.set()
        await complete_finish_job_event.wait()
        return await original_finish_job_run(**arguments)

    connector.finish_job_run = mocker.AsyncMock(name="finish_job_run")
    connector.finish_job_run.side_effect = delayed_finish_job_run

    @app.task(queue="yay", name="task_func")
    async def task_func():
        pass

    job_id = await task_func.defer_async()

    await start_worker(worker)
    # The job is done but its status update is held back.
    await wait_for(finish_job_started_event.is_set)

    await app.job_manager.cancel_job_by_id_async(job_id, abort=True)
    await wait_for(lambda: job_id in worker._job_ids_to_abort)

    complete_finish_job_event.set()

    await wait_for_job_status(app, job_id, Status.SUCCEEDED)


async def test_abort_async_job_preventing_cancellation(app: App, worker):
    """
    Tests that an async job can prevent itself from being aborted
    """

    job_started_event = asyncio.Event()
    never = asyncio.Event()

    @app.task(queue="yay", name="task_func")
    async def task_func():
        job_started_event.set()
        try:
            await never.wait()
        except asyncio.CancelledError:
            pass

    job_id = await task_func.defer_async()

    await start_worker(worker)
    await wait_for(job_started_event.is_set)

    await app.job_manager.cancel_job_by_id_async(job_id, abort=True)

    await wait_for_job_status(app, job_id, Status.SUCCEEDED)


@pytest.mark.parametrize(
    "worker",
    [
        ({"listen_notify": False, "abort_job_polling_interval": 0.05}),
        ({"listen_notify": True, "abort_job_polling_interval": 1}),
    ],
    indirect=["worker"],
)
async def test_run_job_abort(app: App, worker: Worker):
    job_started_event = asyncio.Event()

    @app.task(queue="yay", name="task_func", pass_context=True)
    async def task_func(job_context: JobContext):
        job_started_event.set()
        while True:
            await asyncio.sleep(0.01)
            if job_context.should_abort():
                raise JobAborted()

    job_id = await task_func.defer_async()

    await start_worker(worker)
    await wait_for(job_started_event.is_set)

    await app.job_manager.cancel_job_by_id_async(job_id, abort=True)

    await wait_for_job_status(app, job_id, Status.ABORTED)

    await wait_for(lambda: worker._job_ids_to_abort == {})
    assert worker._job_ids_to_abort == {}, (
        "Expected cancelled job id to be removed from set"
    )


@pytest.mark.parametrize(
    "critical_error, recover_on_attempt_number, expected_status, "
    "expected_attempts, expected_info_logs, expected_error_logs",
    [
        (False, 2, "succeeded", 2, 1, 0),
        (True, 2, "succeeded", 2, 1, 0),
        (False, 3, "failed", 2, 1, 1),
        (True, 3, "failed", 2, 1, 1),
    ],
)
async def test_run_job_retry_failed_job(
    app: App,
    worker,
    critical_error,
    recover_on_attempt_number,
    expected_status,
    expected_attempts,
    expected_info_logs,
    expected_error_logs,
    caplog,
):
    caplog.set_level("INFO")

    worker.wait = False

    attempt = 0

    @app.task(retry=1)
    def task_func():
        nonlocal attempt
        attempt += 1
        if attempt < recover_on_attempt_number:
            raise CustomCriticalError("Nope") if critical_error else ValueError("Nope")

    job_id = await task_func.defer_async()

    run_task = await start_worker(worker)

    # wait=False: the worker exits once it runs out of jobs to process.
    await asyncio.wait_for(run_task, 2)

    connector = cast(InMemoryConnector, app.connector)
    job_row = connector.jobs[job_id]
    assert job_row["status"] == expected_status
    assert job_row["attempts"] == expected_attempts

    info_records = [
        record
        for record in caplog.records
        if record.levelname == "INFO" and "to retry" in record.message
    ]
    error_records = [record for record in caplog.records if record.levelname == "ERROR"]
    assert len(info_records) == expected_info_logs
    assert len(error_records) == expected_error_logs


async def test_run_log_actions(app: App, caplog, worker):
    caplog.set_level("DEBUG")

    done = asyncio.Event()

    @app.task(queue="some_queue")
    def t():
        done.set()

    await t.defer_async()

    await start_worker(worker)

    await asyncio.wait_for(done.wait(), timeout=2)

    connector = cast(InMemoryConnector, app.connector)
    expected_actions = [
        "defer_jobs",
        "prune_stalled_workers",
        "register_worker",
        "fetch_job",
        "finish_job",
        "fetch_job",
    ]

    await wait_for(lambda: len(connector.queries) >= len(expected_actions))

    assert [q[0] for q in connector.queries] == expected_actions

    logs = {(r.action, r.levelname) for r in caplog.records if hasattr(r, "action")}
    # remove the periodic_deferrer_no_task log record because that makes the test flaky
    assert {
        ("about_to_defer_jobs", "DEBUG"),
        ("jobs_deferred", "INFO"),
        ("start_worker", "INFO"),
        ("loaded_job_info", "DEBUG"),
        ("start_job", "INFO"),
        ("job_success", "INFO"),
        ("finish_task", "DEBUG"),
    } <= logs


async def test_run_log_current_job_when_stopping(app: App, worker, caplog):
    caplog.set_level("DEBUG")
    job_started_event = asyncio.Event()
    complete_job_event = asyncio.Event()

    @app.task(queue="some_queue")
    async def t():
        job_started_event.set()
        await complete_job_event.wait()

    job_id = await t.defer_async()
    run_task = await start_worker(worker)
    await wait_for(job_started_event.is_set)

    worker.stop()

    # We want to make sure that the log that names the current running task fired.
    expected_log = (
        f"Waiting for job to finish: worker: tests.unit.test_worker.t[{job_id}]()"
    )
    await wait_for(lambda: any(expected_log in r.message for r in caplog.records))

    complete_job_event.set()
    await asyncio.wait_for(run_task, timeout=2)

    logs = " ".join(r.message for r in caplog.records)
    assert "Stop requested" in logs
    assert expected_log in logs


async def test_run_no_signal_handlers(worker, kill_own_pid):
    worker.install_signal_handlers = False
    await start_worker(worker)
    await wait_for(lambda: worker.worker_id is not None)

    with pytest.raises(KeyboardInterrupt):
        # Test that handlers are NOT installed
        kill_own_pid(signal=signal.SIGINT)


async def test_worker_id_and_heartbeat_lifecycle(app: App):
    connector = cast(InMemoryConnector, app.connector)

    assert connector.workers == {}

    worker = Worker(app, update_heartbeat_interval=0.05)
    assert worker.worker_id is None

    run_task = await start_worker(worker)

    await wait_for(lambda: worker.worker_id is not None)
    worker_id = worker.worker_id
    assert worker_id is not None and worker_id > 0

    await wait_for(lambda: worker_id in connector.workers)
    heartbeat1 = connector.workers[worker_id]
    assert heartbeat1 is not None

    await wait_for(lambda: connector.workers[worker_id] > heartbeat1)

    worker.stop()
    await asyncio.wait_for(run_task, 2)

    assert worker.worker_id is None
    assert connector.workers == {}


async def test_job_receives_worker_id(app: App):
    job_started_event = asyncio.Event()
    complete_job_event = asyncio.Event()

    @app.task(queue="some_queue")
    async def t():
        job_started_event.set()
        await complete_job_event.wait()

    job_id = await t.defer_async()

    connector = cast(InMemoryConnector, app.connector)
    job_row = connector.jobs[job_id]

    assert job_row["worker_id"] is None

    worker = Worker(app, wait=False)
    run_task = await start_worker(worker)

    await wait_for(job_started_event.is_set)

    assert job_row["status"] == "doing"
    assert job_row["worker_id"] == worker.worker_id

    complete_job_event.set()
    await asyncio.wait_for(run_task, 2)

    assert job_row["status"] == "succeeded"
    assert job_row["worker_id"] is None


async def test_worker_prunes_stalled_workers(app: App):
    worker = Worker(app, wait=False)

    worker1_id = 1
    worker2_id = 2

    connector = cast(InMemoryConnector, app.connector)
    connector.workers = {
        worker1_id: utils.utcnow()
        - datetime.timedelta(seconds=worker.stalled_worker_timeout - 1),
        worker2_id: utils.utcnow()
        - datetime.timedelta(seconds=worker.stalled_worker_timeout + 1),
    }

    run_task = await start_worker(worker)
    await asyncio.wait_for(run_task, 2)

    assert worker1_id in connector.workers
    assert worker2_id not in connector.workers


async def test_worker_stops_when_side_task_fails(
    app: App, caplog, mocker: MockerFixture
):
    caplog.set_level("INFO")

    async def failing_update_heartbeat(self):
        raise ValueError("Simulated heartbeat failure")

    mocker.patch.object(Worker, "_update_heartbeat", failing_update_heartbeat)

    worker = Worker(app)
    await worker.run()

    side_task_failed_records = [
        record
        for record in caplog.records
        if hasattr(record, "action") and record.action == "side_task_failed"
    ]

    assert len(side_task_failed_records) == 1
    error_record = side_task_failed_records[0]
    assert "update_heartbeats failed with exception" in error_record.message
    assert "Simulated heartbeat failure" in error_record.message
    assert "stopping worker" in error_record.message
    assert error_record.task_name == "update_heartbeats"
