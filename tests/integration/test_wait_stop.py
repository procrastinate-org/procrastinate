import asyncio
import time

import pytest

from procrastinate import App, jobs


@pytest.mark.asyncio
async def test_wait_for_jobs(pg_job_store, get_all):
    """
    Testing that a new job arriving in the queue interrupts the wait
    """
    pg_job_store.socket_timeout = 2
    await pg_job_store.listen_for_jobs()

    async def defer_job():
        await asyncio.sleep(0.5)
        await pg_job_store.defer_job(
            jobs.Job(id=0, queue="yay", task_name="oh", lock="sher", task_kwargs={})
        )

    before = time.perf_counter()
    await asyncio.gather(pg_job_store.wait_for_jobs(), defer_job())
    after = time.perf_counter()

    # If we wait less than 1 sec, it means the wait didn't reach the timeout.
    assert after - before < 1

    # We *did* create a job
    rows = await(get_all('procrastinate_jobs', 'id'))
    assert len(rows) == 1


@pytest.mark.asyncio
async def test_wait_for_jobs_stop_from_signal(pg_job_store, kill_own_pid):
    """
    Testing than ctrl+c interrupts the wait
    """
    pg_job_store.socket_timeout = 2
    app = App(job_store=pg_job_store)

    async def stop():
        await asyncio.sleep(0.5)
        kill_own_pid()

    before = time.perf_counter()
    await asyncio.gather(app.run_worker_async(), stop())
    after = time.perf_counter()

    # If we wait less than 1 sec, it means the wait didn't reach the timeout.
    assert after - before < 1


@pytest.mark.asyncio
async def test_wait_for_jobs_stop_from_pipe(pg_job_store):
    """
    Testing than calling job_store.stop() interrupts the wait
    """
    # This is a sub-case from above but we never know.
    pg_job_store.socket_timeout = 2
    await pg_job_store.listen_for_jobs()

    async def stop():
        await asyncio.sleep(0.5)
        pg_job_store.stop()

    before = time.perf_counter()
    await asyncio.gather(pg_job_store.wait_for_jobs(), stop())
    after = time.perf_counter()

    # If we wait less than 1 sec, it means the wait didn't reach the timeout.
    assert after - before < 1
