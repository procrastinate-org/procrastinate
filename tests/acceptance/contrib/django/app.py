import time

import procrastinate
from procrastinate.contrib.django.django_connector import DjangoConnector

from ... import app as app_common
from ...param import Param

app = procrastinate.App(
    connector=DjangoConnector(
        json_dumps=app_common.json_dumps, json_loads=app_common.json_loads
    )
)
app.open()

# Check that tasks can be added from blueprints
bp = procrastinate.Blueprint()


@bp.task(queue="default")
def sum_task(a, b):
    print(a + b)


app.add_tasks_from(bp, namespace="ns")
app.add_task_alias(sum_task, "tests.acceptance.contrib.django.app.sum_task")


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
