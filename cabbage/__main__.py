import sys
import logging

from cabbage import worker, tasks

logger = logging.getLogger(__name__)
task_manager = tasks.TaskManager()


@task_manager.task(queue="sums")
def sum(task_run, a, b):
    with open(f"{task_run.task.name}-{task_run.id}", "w") as f:
        f.write(f"{a + b}")


@task_manager.task(queue="sums")
def sum_plus_one(task_run, a, b):
    with open(f"{task_run.task.name}-{task_run.id}", "w") as f:
        f.write(f"{a + b + 1}")


@tasks.Task(manager=task_manager, queue="products")
def product(task_run, a, b):
    with open(f"{task_run.task.name}-{task_run.id}", "w") as f:
        f.write(f"{a * b}")


def client():
    sum.defer(a=3, b=5)
    sum.defer(a=5, b=7)
    sum_plus_one.defer(a=4, b=7)
    product.defer(a=2, b=8)


def main():
    logging.basicConfig(level="DEBUG")
    process = sys.argv[1]
    if process == "worker":
        return worker.worker(task_manager, "sums")
    else:
        return client()


if __name__ == "__main__":
    main()
