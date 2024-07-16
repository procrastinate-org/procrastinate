from __future__ import annotations

import asyncio
import contextlib
import signal
from typing import TYPE_CHECKING, cast

import pytest

from procrastinate import worker
from procrastinate.testing import InMemoryConnector

if TYPE_CHECKING:
    from procrastinate import App


# how long to wait before considering the test a fail
timeout = 0.05


async def _wait_on_cancelled(task: asyncio.Task, timeout: float):
    try:
        await asyncio.wait_for(task, timeout=timeout)
    except asyncio.CancelledError:
        pass
    except asyncio.TimeoutError:
        pytest.fail("Failed to launch task within f{timeout}s")


@contextlib.asynccontextmanager
async def running_worker(app: App):
    running_worker = worker.Worker(app=app, queues=["some_queue"])
    task = asyncio.ensure_future(running_worker.run())
    yield running_worker, task
    running_worker.stop()
    await _wait_on_cancelled(task, timeout=timeout)


async def test_run(app: App, caplog):
    caplog.set_level("DEBUG")

    done = asyncio.Event()

    @app.task(queue="some_queue")
    def t():
        done.set()

    async with running_worker(app):
        await t.defer_async()

        try:
            await asyncio.wait_for(done.wait(), timeout=timeout)
        except asyncio.TimeoutError:
            pytest.fail(f"Failed to launch task withing {timeout}s")

    connector = cast(InMemoryConnector, app.connector)
    assert [q[0] for q in connector.queries] == [
        "defer_job",
        "fetch_job",
        "finish_job",
    ]

    logs = {(r.action, r.levelname) for r in caplog.records}
    # remove the periodic_deferrer_no_task log record because that makes the test flaky
    assert {
        ("about_to_defer_job", "DEBUG"),
        ("job_defer", "INFO"),
        ("loaded_job_info", "DEBUG"),
        ("start_job", "INFO"),
        ("job_success", "INFO"),
        ("finish_task", "DEBUG"),
    } <= logs


async def test_run_log_current_job_when_stopping(app: App, caplog):
    caplog.set_level("DEBUG")

    async with running_worker(app) as (worker, worker_task):

        @app.task(queue="some_queue")
        async def t():
            worker.stop()

        await t.defer_async()

        with pytest.raises(asyncio.CancelledError):
            try:
                await asyncio.wait_for(worker_task, timeout=timeout)
            except asyncio.TimeoutError:
                pytest.fail("Failed to launch task within f{timeout}s")

    # We want to make sure that the log that names the current running task fired.
    logs = " ".join(r.message for r in caplog.records)
    assert "Stop requested" in logs
    assert (
        "Waiting for job to finish: worker 0: tests.integration.test_worker.t[1]()"
        in logs
    )


async def test_run_no_listen_notify(app: App):
    running_worker = worker.Worker(app=app, queues=["some_queue"], listen_notify=False)
    task = asyncio.ensure_future(running_worker.run())
    try:
        await asyncio.sleep(0.01)
        connector = cast(InMemoryConnector, app.connector)
        assert connector.notify_event is None
    finally:
        running_worker.stop()
        await _wait_on_cancelled(task, timeout=timeout)


async def test_run_no_signal_handlers(app: App, kill_own_pid):
    running_worker = worker.Worker(
        app=app, queues=["some_queue"], install_signal_handlers=False
    )

    task = asyncio.ensure_future(running_worker.run())
    try:
        with pytest.raises(KeyboardInterrupt):
            await asyncio.sleep(0.01)
            # Test that handlers are NOT installed
            kill_own_pid(signal=signal.SIGINT)
    finally:
        running_worker.stop()
        await _wait_on_cancelled(task, timeout)
