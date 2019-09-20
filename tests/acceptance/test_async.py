import signal
import threading
import time

import pytest

import procrastinate

pytestmark = pytest.mark.asyncio


@pytest.fixture
def app(aiopg_job_store):
    return procrastinate.App(job_store=aiopg_job_store)


async def test_nominal(app, kill_own_pid, caplog):

    caplog.set_level("DEBUG")

    sum_results = []
    product_results = []

    @app.task(queue="default")
    def sum_task(a, b):
        sum_results.append(a + b)

    @app.task()
    def increment_task(a):
        sum_results.append(a + 1)

    @app.task
    def stop_task():
        kill_own_pid(signal.SIGINT)

    @app.task(queue="product_queue")
    def product_task(a, b):
        product_results.append(a * b)

    @app.task(queue="product_queue")
    def stop_task_product_queue():
        kill_own_pid(signal.SIGTERM)

    nb_tries = 0

    @app.task(queue="retry", retry=10)
    def two_fails():
        nonlocal nb_tries
        if nb_tries < 2:
            nb_tries += 1
            raise Exception("This should fail")

        kill_own_pid(signal.SIGINT)

    await sum_task.defer(a=5, b=7)
    '''await sum_task.defer(a=3, b=4)
    await increment_task.defer(a=3)
    await product_task.defer(a=5, b=4)
    await stop_task_product_queue.defer()
    await two_fails.defer()'''

    def stop():
        time.sleep(1)
        sum_task.defer(a=2, b=3)
        stop_task.defer()

    thread = threading.Thread(target=stop)
    thread.start()

    app.run_worker(queues=["default"])

    assert sum_results == [12, 7, 4, 5]
    assert product_results == []

    app.run_worker(queues=["product_queue"])

    assert sum_results == [12, 7, 4, 5]
    assert product_results == [20]

    assert nb_tries == 0
    app.run_worker(queues=["retry"])
    assert nb_tries == 2

