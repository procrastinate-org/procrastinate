import random

from procrastinate_demo.procrastinate_app import app


@app.task(queue="sums")
def sum(a, b):
    print(a + b)


@app.task(queue="sleep")
def sleep(i):
    import time

    time.sleep(i)


@app.task(queue="sums")
def sum_plus_one(a, b):
    print(a + b + 1)


@app.task(queue="retry", retry=100)
def random_fail():
    if random.random() > 0.1:
        raise Exception("random fail")
