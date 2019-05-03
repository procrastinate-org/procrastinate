import signal
import threading
import time

import cabbage


def test_nominal(connection, kill_own_pid, caplog):
    job_store = cabbage.PostgresJobStore(connection=connection)
    task_manager = cabbage.TaskManager(job_store=job_store)

    caplog.set_level("DEBUG")

    sum_results = []
    product_results = []

    @task_manager.task(queue="sum_queue")
    def sum_task(a, b):
        sum_results.append(a + b)

    @task_manager.task(queue="sum_queue")
    def increment_task(a):
        sum_results.append(a + 1)

    @task_manager.task(queue="sum_queue")
    def stop_sum():
        kill_own_pid(signal.SIGINT)

    @task_manager.task(queue="product_queue")
    def product_task(a, b):
        product_results.append(a * b)

    @task_manager.task(queue="product_queue")
    def stop_product():
        kill_own_pid(signal.SIGTERM)

    sum_task.defer(a=5, b=7)
    sum_task.defer(a=3, b=4)
    increment_task.defer(a=3)
    product_task.defer(a=5, b=4)
    stop_product.defer()

    def stop():
        time.sleep(1)
        sum_task.defer(a=2, b=3)
        stop_sum.defer()

    thread = threading.Thread(target=stop)
    thread.start()

    cabbage.Worker(task_manager, "sum_queue").run(timeout=1e-9)

    assert sum_results == [12, 7, 4, 5]
    assert product_results == []

    cabbage.Worker(task_manager, "product_queue").run(timeout=1e-9)

    assert sum_results == [12, 7, 4, 5]
    assert product_results == [20]


def test_lock(connection, caplog):
    """
    In this test, we launch 2 workers in two parallel threads, and ask them
    both to process tasks with the same lock. We check that the second task is
    not started before the first one was finished.
    """
    caplog.set_level("DEBUG")

    job_store = cabbage.PostgresJobStore(connection=connection)
    task_manager = cabbage.TaskManager(job_store=job_store)

    task_order = []

    @task_manager.task(queue="queue")
    def sleep_and_write(sleep, write_before, write_after):
        task_order.append(write_before)
        time.sleep(sleep)
        task_order.append(write_after)

    workers = []

    def launch_worker():
        worker = cabbage.Worker(task_manager, "queue")
        workers.append(worker)
        worker.run(timeout=1e-9)

    thread1 = threading.Thread(target=launch_worker)
    thread1.start()
    thread2 = threading.Thread(target=launch_worker)
    thread2.start()

    job_template = sleep_and_write.configure(lock="sher")

    job_template.defer(sleep=1, write_before="before-1", write_after="after-1")
    job_template.defer(sleep=0, write_before="before-2", write_after="after-2")

    time.sleep(1.1)
    for worker in workers:
        worker.stop()

    thread1.join()
    thread2.join()

    assert task_order == ["before-1", "after-1", "before-2", "after-2"]
