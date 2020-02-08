import asyncio
import time

import pytest

from procrastinate import App, jobs, store


@pytest.mark.asyncio
async def test_wait_for_activity(pg_connector):
    """
    Testing that a new job arriving in the queue interrupts the wait
    """
    pg_connector.socket_timeout = 2
    job_store = store.JobStore(connector=pg_connector)
    await job_store.listen_for_jobs()

    async def defer_job():
        await asyncio.sleep(0.5)
        await job_store.defer_job(
            jobs.Job(id=0, queue="yay", task_name="oh", lock="sher", task_kwargs={})
        )

    before = time.perf_counter()
    await asyncio.gather(pg_connector.wait_for_activity(), defer_job())
    after = time.perf_counter()

    # If we wait less than 1 sec, it means the wait didn't reach the timeout.
    assert after - before < 1

    # We *did* create a job
    assert await job_store.fetch_job(queues=None)


@pytest.mark.asyncio
async def test_wait_for_activity_timeout(pg_connector):
    """
    Testing that we timeout if nothing happens
    """
    pg_connector.socket_timeout = 0.01

    before = time.perf_counter()
    await pg_connector.wait_for_activity()
    after = time.perf_counter()

    assert after - before < 0.1


@pytest.mark.asyncio
async def test_wait_for_activity_stop_from_signal(pg_connector, kill_own_pid):
    """
    Testing than ctrl+c interrupts the wait
    """
    pg_connector.socket_timeout = 2
    app = App(connector=pg_connector)

    async def stop():
        await asyncio.sleep(0.5)
        kill_own_pid()

    before = time.perf_counter()
    await asyncio.gather(app.run_worker_async(), stop())
    after = time.perf_counter()

    # If we wait less than 1 sec, it means the wait didn't reach the timeout.
    assert after - before < 1


@pytest.mark.asyncio
async def test_wait_for_activity_stop_from_pipe(pg_connector):
    """
    Testing than calling job_store.stop() interrupts the wait
    """
    # This is a sub-case from above but we never know.
    pg_connector.socket_timeout = 2
    job_store = store.JobStore(connector=pg_connector)

    await job_store.listen_for_jobs()

    async def stop():
        await asyncio.sleep(0.5)
        pg_connector.interrupt_wait()

    before = time.perf_counter()
    await asyncio.gather(pg_connector.wait_for_activity(), stop())
    after = time.perf_counter()

    # If we wait less than 1 sec, it means the wait didn't reach the timeout.
    assert after - before < 1
