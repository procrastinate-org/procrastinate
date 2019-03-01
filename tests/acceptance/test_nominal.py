import cabbage


def test_nominal(db, mocker):
    # we can't wait infinitly, let's just apply the function!
    mocker.patch("cabbage.task_worker.infinite_loop", side_effect=lambda x: x())

    task_manager = cabbage.TaskManager()

    sum_results = []
    product_results = []

    @task_manager.task(queue="sum_queue")
    def sum_task(task_run, a, b):  # pytest: disable=unused-argument
        sum_results.append(a + b)

    @task_manager.task(queue="sum_queue")
    def increment_task(task_run, a):  # pytest: disable=unused-argument
        sum_results.append(a + 1)

    @task_manager.task(queue="product_queue")
    def product_task(task_run, a, b):  # pytest: disable=unused-argument
        product_results.append(a * b)

    sum_task.defer(a=5, b=7)
    sum_task.defer(a=3, b=4)
    increment_task.defer(a=3)
    product_task.defer(a=5, b=4)

    cabbage.worker(task_manager=task_manager, queue="sum_queue", timeout=1e-9)

    assert sum_results == [12, 7, 4]
    assert product_results == []

    cabbage.worker(task_manager=task_manager, queue="product_queue", timeout=1e-9)

    assert sum_results == [12, 7, 4]
    assert product_results == [20]
