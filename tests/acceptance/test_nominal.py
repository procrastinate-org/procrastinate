import cabbage


def test_nominal(connection):
    task_manager = cabbage.TaskManager()

    sum_results = []
    product_results = []

    @task_manager.task(queue="sum_queue")
    def sum_task(task_run, a, b):  # pytest: disable=unused-argument
        sum_results.append(a + b)

    @task_manager.task(queue="sum_queue")
    def increment_task(task_run, a):  # pytest: disable=unused-argument
        sum_results.append(a + 1)

    @task_manager.task(queue="sum_queue")
    def stop_sum(task_run):
        raise KeyboardInterrupt()

    @task_manager.task(queue="product_queue")
    def product_task(task_run, a, b):  # pytest: disable=unused-argument
        product_results.append(a * b)

    @task_manager.task(queue="product_queue")
    def stop_product(task_run):
        raise KeyboardInterrupt()

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
