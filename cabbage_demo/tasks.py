from cabbage_demo.cabbage_app import app


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
