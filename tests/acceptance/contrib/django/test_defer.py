import pytest
from django.db import transaction

pytestmark = pytest.mark.asyncio


def test_defer_should_create_job_on_transaction_atomic_commit(django_app):
    sum_results = []
    product_results = []

    @django_app.task(queue="default", name="sum_task")
    def sum_task(a, b):
        sum_results.append(a + b)

    @django_app.task(queue="default", name="product_task")
    def product_task(a, b):
        product_results.append(a * b)

    with transaction.atomic():
        sum_task.defer(a=1, b=2)
        sum_task.configure().defer(a=3, b=4)
        django_app.configure_task(name="sum_task").defer(a=5, b=6)
        product_task.defer(a=3, b=4)

    django_app.run_worker(queues=["default"], wait=False)

    assert sum_results == [3, 7, 11]
    assert product_results == [12]


def test_defer_should_not_create_job_when_transaction_atomic_rollback(django_app):
    sum_results = []
    product_results = []

    @django_app.task(queue="default", name="sum_task")
    def sum_task(a, b):
        sum_results.append(a + b)

    @django_app.task(queue="default", name="product_task")
    def product_task(a, b):
        product_results.append(a * b)

    try:
        with transaction.atomic():
            sum_task.defer(a=1, b=2)
            sum_task.configure().defer(a=3, b=4)
            django_app.configure_task(name="sum_task").defer(a=5, b=6)
            product_task.defer(a=3, b=4)
            raise ValueError("Rollback transaction")
    except ValueError:
        pass

    django_app.run_worker(queues=["default"], wait=False)

    assert sum_results == []
    assert product_results == []


def test_defer_inside_task_should_create_job_on_transaction_atomic_commit(django_app):
    sum_results = []
    product_results = []

    @django_app.task(queue="default", name="sum_task")
    def sum_task(a, b):
        sum_results.append(a + b)
        with transaction.atomic():
            product_task.defer(a=a, b=b)

    @django_app.task(queue="default", name="product_task")
    def product_task(a, b):
        product_results.append(a * b)

    sum_task.defer(a=1, b=2)
    sum_task.configure().defer(a=3, b=4)
    django_app.configure_task(name="sum_task").defer(a=5, b=6)

    django_app.run_worker(queues=["default"], wait=False)

    assert sum_results == [3, 7, 11]
    assert product_results == [2, 12, 30]


def test_defer_inside_task_should_not_create_job_on_transaction_atomic_rollback(
    django_app,
):
    sum_results = []
    product_results = []

    @django_app.task(queue="default", name="sum_task")
    def sum_task(a, b):
        sum_results.append(a + b)
        try:
            with transaction.atomic():
                product_task.defer(a=a, b=b)
                raise ValueError("Rollback transaction")
        except ValueError:
            pass

    @django_app.task(queue="default", name="product_task")
    def product_task(a, b):
        product_results.append(a * b)

    sum_task.defer(a=1, b=2)
    sum_task.configure().defer(a=3, b=4)
    django_app.configure_task(name="sum_task").defer(a=5, b=6)

    django_app.run_worker(queues=["default"], wait=False)

    assert sum_results == [3, 7, 11]
    assert product_results == []
