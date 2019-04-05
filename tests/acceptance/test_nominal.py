import signal

import cabbage


def test_nominal(connection, kill_own_pid):
    task_manager = cabbage.TaskManager(connection=connection)

    sum_results = []
    product_results = []

    @task_manager.task(queue="sum_queue")
    def sum_task(a, b):  # pytest: disable=unused-argument
        sum_results.append(a + b)

    @task_manager.task(queue="sum_queue")
    def increment_task(a):  # pytest: disable=unused-argument
        sum_results.append(a + 1)

    @task_manager.task(queue="sum_queue")
    def stop_sum():
        kill_own_pid(signal.SIGINT)

    @task_manager.task(queue="product_queue")
    def product_task(a, b):  # pytest: disable=unused-argument
        product_results.append(a * b)

    @task_manager.task(queue="product_queue")
    def stop_product():
        kill_own_pid(signal.SIGTERM)

    sum_task.defer(a=5, b=7)
    sum_task.defer(a=3, b=4)
    increment_task.defer(a=3)
    stop_sum.defer()
    product_task.defer(a=5, b=4)
    stop_product.defer()

    cabbage.Worker(task_manager, "sum_queue").run(timeout=1e-9)

    assert sum_results == [12, 7, 4]
    assert product_results == []

    cabbage.Worker(task_manager, "product_queue").run(timeout=1e-9)

    assert sum_results == [12, 7, 4]
    assert product_results == [20]
