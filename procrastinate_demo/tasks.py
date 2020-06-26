import random

from procrastinate_demo.app import app


@app.task(queue="sums")
def sum(a, b):
    return a + b


@app.task(queue="sleep")
async def sleep(i):
    import asyncio

    await asyncio.sleep(i)


@app.task(queue="sums")
def sum_plus_one(a, b):
    return a + b + 1


@app.task(queue="retry", retry=100)
def random_fail():
    if random.random() > 0.1:
        raise Exception("random fail")


# 6th * means "every second of the minute"
@app.periodic(cron="* * * * * *")
@app.task
def tick(timestamp):
    return timestamp
