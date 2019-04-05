import logging
import sys

import cabbage

logger = logging.getLogger(__name__)
task_manager = cabbage.TaskManager()


@task_manager.task(queue="sums")
def sum(a, b):
    print(a + b)


@task_manager.task(queue="sums")
def sleep(i):
    import time

    time.sleep(i)


@task_manager.task(queue="sums")
def sum_plus_one(a, b):
    print(a + b + 1)


def client():
    # sum.defer(a=3, b=5)
    # sum.defer(a=5, b=7)
    # sum.defer(a=5, b="a")
    # sum_plus_one.defer(a=4, b=7)
    # product.defer(a=2, b=8)
    sleep.defer(lock="a", i=2)
    sleep.defer(lock="a", i=3)
    sleep.defer(lock="a", i=4)


def main():
    logging.basicConfig(level="DEBUG")
    process = sys.argv[1]
    if process == "worker":
        queue = sys.argv[2]
        return cabbage.task_worker.Worker(task_manager, queue).run()
    else:
        return client()


if __name__ == "__main__":
    main()
