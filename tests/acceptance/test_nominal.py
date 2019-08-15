import signal
import threading
import time

import pytest

import procrastinate


@pytest.fixture
def app(pg_job_store):
    return procrastinate.App(job_store=pg_job_store)


def test_nominal(app, kill_own_pid, caplog):

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
    def stop_sum():
        kill_own_pid(signal.SIGINT)

    @app.task(queue="product_queue")
    def product_task(a, b):
        product_results.append(a * b)

    @app.task(queue="product_queue")
    def stop_product():
        kill_own_pid(signal.SIGTERM)

    nb_tries = 0

    @app.task(queue="retry", retry=10)
    def two_fails():
        nonlocal nb_tries
        if nb_tries < 2:
            nb_tries += 1
            raise Exception("This should fail")

        kill_own_pid(signal.SIGINT)

    sum_task.defer(a=5, b=7)
    sum_task.defer(a=3, b=4)
    increment_task.defer(a=3)
    product_task.defer(a=5, b=4)
    stop_product.defer()
    two_fails.defer()

    def stop():
        time.sleep(1)
        sum_task.defer(a=2, b=3)
        stop_sum.defer()

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


def test_lock(app, caplog):
    """
    In this test, we launch 2 workers in two parallel threads, and ask them
    both to process tasks with the same lock. We check that the second task is
    not started before the first one was finished.
    """
    caplog.set_level("DEBUG")

    task_order = []

    @app.task(queue="queue")
    def sleep_and_write(sleep, write_before, write_after):
        task_order.append(write_before)
        time.sleep(sleep)
        task_order.append(write_after)

    workers = []

    def launch_worker():
        worker = app._worker()
        workers.append(worker)
        worker.run()

    thread1 = threading.Thread(target=launch_worker)
    thread2 = threading.Thread(target=launch_worker)

    job_template = sleep_and_write.configure(lock="sher")

    job_template.defer(sleep=1, write_before="before-1", write_after="after-1")
    job_template.defer(sleep=0.001, write_before="before-2", write_after="after-2")

    thread1.start()
    thread2.start()

    time.sleep(1.1)
    for worker in workers:
        worker.stop()

    thread1.join()
    thread2.join()

    assert task_order == ["before-1", "after-1", "before-2", "after-2"]
