import functools
import itertools
import json
import time

import procrastinate

from .param import Param


def encode(obj):
    if isinstance(obj, Param):
        return obj.p
    raise TypeError()


def decode(dct):
    if "p1" in dct:
        dct["p1"] = Param(dct["p1"])
    if "p2" in dct:
        dct["p2"] = Param(dct["p2"])
    return dct


json_dumps = functools.partial(json.dumps, default=encode)
json_loads = functools.partial(json.loads, object_hook=decode)

app = procrastinate.App(
    connector=procrastinate.AiopgConnector(json_dumps=json_dumps, json_loads=json_loads)
)
app.open()

sync_app = procrastinate.App(
    connector=procrastinate.Psycopg2Connector(
        json_dumps=json_dumps, json_loads=json_loads
    )
)
sync_app.open()


@app.task(queue="default")
def sum_task(a, b):
    print(a + b)


@app.task(queue="default")
def sum_task_param(p1: Param, p2: Param):
    if not isinstance(p1, Param):
        raise Exception("wrong type for p1")
    if not isinstance(p2, Param):
        raise Exception("wrong type for p2")
    print(p1 + p2)


@app.task()
def increment_task(a):
    print(a + 1)


@app.task(queue="product_queue")
def product_task(a, b):
    print(a * b)


nb_tries = 0


@app.task(queue="retry", retry=10)
def two_fails():
    global nb_tries
    if nb_tries < 2:
        nb_tries += 1
        raise Exception("This should fail")
    # The subprocess will print, the main process will analyze stdout
    print("Print something to stdout")


nb_tries_multiple_exception_failures = 0


@app.task(
    queue="retry",
    retry=procrastinate.RetryStrategy(retry_exceptions=[ValueError, KeyError]),
)
def multiple_exception_failures():
    global nb_tries_multiple_exception_failures
    print(f"Try {nb_tries_multiple_exception_failures}")
    exception = [ValueError(), KeyError(), AttributeError(), ValueError()][
        nb_tries_multiple_exception_failures
    ]
    nb_tries_multiple_exception_failures += 1
    raise exception


@app.task(queue="lock_test")
def sleep_and_write(sleep, write_before, write_after):
    print("->", write_before, time.time())
    time.sleep(sleep)
    print("->", write_after, time.time())


cron_app = procrastinate.App(
    connector=procrastinate.AiopgConnector(json_dumps=json_dumps, json_loads=json_loads)
)


counter = itertools.count()


@cron_app.periodic(cron="* * * * * *")
@cron_app.task()
def tick(timestamp):
    print("tick", next(counter), timestamp)
