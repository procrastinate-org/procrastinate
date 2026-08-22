from __future__ import annotations

import asyncio
import signal

import pytest

from procrastinate import app
from procrastinate import worker as worker_module


async def wait_for_signal_handler(sig: signal.Signals, previous, timeout: float = 5):
    """
    Wait until the worker has installed its handler for `sig`, i.e. until the signal
    has stopped being fatal to this process.

    asyncio's add_signal_handler() also registers a placeholder through
    signal.signal(), so the disposition changing is what tells us the signal is now
    handled. Should that ever stop being true, this times out and fails the test
    rather than letting the signal kill the test process.
    """

    async def poll():
        while signal.getsignal(sig) is previous:
            await asyncio.sleep(0.01)

    await asyncio.wait_for(poll(), timeout)


async def test_wait_for_activity_cancelled(psycopg_connector):
    """
    Testing that the work can be cancelled
    """
    pg_app = app.App(connector=psycopg_connector)
    worker = worker_module.Worker(app=pg_app, fetch_job_polling_interval=2)
    task = asyncio.ensure_future(worker.run())
    await asyncio.sleep(0.2)  # should be enough so that we're waiting

    task.cancel()

    try:
        with pytest.raises(asyncio.CancelledError):
            await asyncio.wait_for(task, timeout=0.2)
    except asyncio.TimeoutError:
        pytest.fail("Failed to stop worker within .2s")


async def test_wait_for_activity_timeout(psycopg_connector):
    """
    Testing that we timeout if nothing happens
    """
    pg_app = app.App(connector=psycopg_connector)
    worker = worker_module.Worker(app=pg_app, fetch_job_polling_interval=2)
    task = asyncio.ensure_future(worker.run())
    await asyncio.sleep(0.2)  # should be enough so that we're waiting
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(task, timeout=0.2)


async def test_wait_for_activity_stop_from_signal(psycopg_connector, kill_own_pid):
    """
    Testing than ctrl+c interrupts the wait
    """
    pg_app = app.App(connector=psycopg_connector)
    worker = worker_module.Worker(app=pg_app, fetch_job_polling_interval=2)
    # The worker installs its signal handler only after registering itself in the
    # database. Until then SIGTERM is fatal, so betting a fixed delay on those
    # queries means a slow database kills the test process (exit code 143) instead
    # of failing the test.
    previous_handler = signal.getsignal(signal.SIGTERM)
    task = asyncio.ensure_future(worker.run())
    await wait_for_signal_handler(signal.SIGTERM, previous_handler)

    await asyncio.sleep(0.2)  # should be enough so that we're waiting

    kill_own_pid()

    try:
        await asyncio.wait_for(task, timeout=0.2)
    except asyncio.TimeoutError:
        pytest.fail("Failed to stop worker within .2s")


async def test_wait_for_activity_stop(psycopg_connector):
    """
    Testing than calling worker.stop() interrupts the wait
    """
    pg_app = app.App(connector=psycopg_connector)
    worker = worker_module.Worker(app=pg_app, fetch_job_polling_interval=2)
    task = asyncio.ensure_future(worker.run())
    await asyncio.sleep(0.2)  # should be enough so that we're waiting

    worker.stop()

    try:
        await asyncio.wait_for(task, timeout=0.2)
    except asyncio.TimeoutError:
        pytest.fail("Failed to stop worker within .2s")
