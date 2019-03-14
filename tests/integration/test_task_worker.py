import pytest

from cabbage.tasks import TaskManager
from cabbage.task_worker import Worker


@pytest.fixture()
def results():
    return {"sums": [], "products": []}


@pytest.fixture()
def task_manager(connection, results):
    manager = TaskManager(connection)

    @manager.task(queue="sum_queue")
    def sum_task(_, a, b):
        results["sums"].append(a + b)

    @manager.task(queue="sum_queue")
    def stop_task(_):
        raise KeyboardInterrupt()

    sum_task.defer(a=1, b=2)
    stop_task.defer()

    return manager


@pytest.fixture()
def worker(task_manager):
    return Worker(task_manager, "sum_queue")


def test_run(worker, results):
    worker.run()

    assert [3] == results["sums"]
