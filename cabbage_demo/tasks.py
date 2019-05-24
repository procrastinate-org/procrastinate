from cabbage_demo.cabbage_app import task_manager


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
