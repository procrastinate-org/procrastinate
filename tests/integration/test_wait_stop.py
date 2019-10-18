import threading
import time

import pytest

from procrastinate import App, PostgresJobStore, jobs


def test_wait_for_jobs(pg_job_store, connection_params):
    """
    Testing that a new job arriving in the queue interrupts the wait
    """
    pg_job_store.socket_timeout = 2
    pg_job_store.listen_for_jobs()

    def stop():
        time.sleep(0.5)
        try:
            inner_job_store = PostgresJobStore(**connection_params)

            inner_job_store.defer_job(
                jobs.Job(id=0, queue="yay", task_name="oh", lock="sher", task_kwargs={})
            )
        finally:
            inner_job_store.connection.close()

    thread = threading.Thread(target=stop)
    thread.start()

    before = time.perf_counter()
    pg_job_store.wait_for_jobs()
    after = time.perf_counter()

    # If we wait less than 1 sec, it means the wait didn't reach the timeout.
    assert after - before < 1


@pytest.mark.skip("We'll investigate later")
def test_wait_for_jobs_stop_from_signal(pg_job_store, kill_own_pid):
    """
    Testing than ctrl+c interrupts the wait
    """
    pg_job_store.socket_timeout = 2
    app = App(job_store=pg_job_store)

    def stop():
        time.sleep(0.5)
        kill_own_pid()

    thread = threading.Thread(target=stop)
    thread.start()

    before = time.perf_counter()
    app.run_worker()
    after = time.perf_counter()

    # If we wait less than 1 sec, it means the wait didn't reach the timeout.
    assert after - before < 1


@pytest.mark.asyncio
@pytest.mark.skip("We'll investigate later")
async def test_wait_for_jobs_stop_from_pipe(pg_job_store):
    """
    Testing than calling job_store.stop() interrupts the wait
    """
    # This is a sub-case from above but we never know.
    pg_job_store.socket_timeout = 2
    await pg_job_store.listen_for_jobs()

    def stop():
        time.sleep(0.5)
        pg_job_store.stop()

    thread = threading.Thread(target=stop)
    thread.start()

    before = time.perf_counter()
    await pg_job_store.wait_for_jobs()
    after = time.perf_counter()

    # If we wait less than 1 sec, it means the wait didn't reach the timeout.
    assert after - before < 1
