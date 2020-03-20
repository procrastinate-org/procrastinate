import asyncio
import time

import pytest

from procrastinate import App, jobs, store


@pytest.mark.asyncio
async def test_listen_for_jobs(pg_connector):
    """
    Testing that a new job arriving in the queue interrupts the wait
    """
    pg_connector.socket_timeout = 2
    job_store = store.JobStore(connector=pg_connector)

    notify_event = asyncio.Event()
    listen_event = asyncio.Event()

    task = asyncio.create_task(
        job_store.listen_for_jobs(notify_event=notify_event, listen_event=listen_event)
    )
    await listen_event.wait()

    async def defer_job():
        await asyncio.sleep(0.5)
        await job_store.defer_job(
            jobs.Job(id=0, queue="yay", task_name="oh", lock="sher", task_kwargs={})
        )

    before = time.perf_counter()
    await asyncio.gather(notify_event.wait(), defer_job())
    after = time.perf_counter()

    # We can cancel the listen_notify asyncio task at this point
    task.cancel()

    # Test that we didn't wait more that 1 sec
    assert after - before < 1

    # We *did* create a job
    assert await job_store.fetch_job(queues=None)


@pytest.mark.asyncio
async def test_listen_for_jobs_stop_from_signal(pg_connector, kill_own_pid):
    """
    Testing than ctrl+c interrupts the wait
    """
    app = App(connector=pg_connector)

    async def stop():
        await asyncio.sleep(0.5)
        kill_own_pid()

    before = time.perf_counter()
    await asyncio.gather(app.run_worker_async(), stop())
    after = time.perf_counter()

    # If we wait less than 1 sec, it means the wait didn't reach the timeout.
    assert after - before < 1
