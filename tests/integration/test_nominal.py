from psycopg2.extras import RealDictCursor

import cabbage
from cabbage.worker import process_tasks


def test_nominal(db):
    task_manager = cabbage.TaskManager()

    result = []

    @task_manager.task(queue="sum_queue")
    def sum_task(task_run, a, b):
        result.append(a + b)

    sum_task.defer(a=5, b=7)

    with db.cursor(cursor_factory=RealDictCursor) as curs:
        process_tasks(task_manager=task_manager, queue="sum_queue", curs=curs)

    assert result == [12]
