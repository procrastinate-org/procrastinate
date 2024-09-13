from __future__ import annotations

import asyncio

import pytest

from procrastinate import app
from procrastinate import worker as worker_module


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
    task = asyncio.ensure_future(worker.run())
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
