from psycopg2.extras import RealDictCursor

import cabbage
from cabbage.worker import process_tasks


def test_nominal(db):
    task_manager = cabbage.TaskManager()

    sum_results = []
    product_results = []

    @task_manager.task(queue="sum_queue")
    def sum_task(task_run, a, b):
        sum_results.append(a + b)

    @task_manager.task(queue="sum_queue")
    def increment_task(task_run, a):
        sum_results.append(a + 1)

    @task_manager.task(queue="product_queue")
    def product_task(task_run, a, b):
        product_results.append(a * b)

    sum_task.defer(a=5, b=7)
    sum_task.defer(a=3, b=4)
    increment_task.defer(a=3)
    product_task.defer(a=5, b=4)

    with db.cursor(cursor_factory=RealDictCursor) as curs:
        process_tasks(task_manager=task_manager, queue="sum_queue", curs=curs)

    assert sum_results == [12, 7, 4]
    assert product_results == []

    with db.cursor(cursor_factory=RealDictCursor) as curs:
        process_tasks(task_manager=task_manager, queue="product_queue", curs=curs)

    assert sum_results == [12, 7, 4]
    assert product_results == [20]
