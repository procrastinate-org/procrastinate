from __future__ import annotations

import datetime

import freezegun
import pytest

from procrastinate.contrib.django import app
from procrastinate.contrib.django.models import ProcrastinateJob


@app.task(queue="pytest_plugin_queue")
def my_test_task_plugin(a: int, b: int) -> int:
    return a + b


TASK_NAME = "tests.integration.contrib.django.test_pytest_plugin.my_test_task_plugin"


@pytest.fixture(autouse=True)
def clear_jobs(settings):
    settings.PROCRASTINATE_READONLY_MODELS = False
    ProcrastinateJob.objects.all().delete()


@pytest.mark.django_db(transaction=True)
def test_run_procrastinate_jobs(run_procrastinate_jobs):
    my_test_task_plugin.defer(a=3, b=4)

    assert ProcrastinateJob.objects.filter(task_name=TASK_NAME).count() == 1

    run_procrastinate_jobs()

    # Check the job succeeded
    assert (
        ProcrastinateJob.objects.filter(
            task_name=TASK_NAME,
            status="succeeded",
        ).count()
        == 1
    )


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_arun_procrastinate_jobs(arun_procrastinate_jobs):
    await my_test_task_plugin.defer_async(a=5, b=6)

    assert await ProcrastinateJob.objects.filter(task_name=TASK_NAME).acount() == 1

    await arun_procrastinate_jobs()

    # Check the job succeeded
    assert (
        await ProcrastinateJob.objects.filter(
            task_name=TASK_NAME,
            status="succeeded",
        ).acount()
        == 1
    )


@pytest.mark.django_db(transaction=True)
def test_run_procrastinate_jobs_time_travel(run_procrastinate_jobs):
    with freezegun.freeze_time("2025-01-01T00:00:00Z"):
        my_test_task_plugin.defer(a=3, b=4)
        ProcrastinateJob.objects.update(
            scheduled_at=datetime.datetime(
                2025, 1, 2, 0, 0, 0, tzinfo=datetime.timezone.utc
            )
        )

        assert (
            ProcrastinateJob.objects.filter(
                task_name=TASK_NAME,
                status="todo",
            ).count()
            == 1
        )

        # worker shouldn't pick it up yet
        run_procrastinate_jobs()
        assert (
            ProcrastinateJob.objects.filter(
                task_name=TASK_NAME,
                status="todo",
            ).count()
            == 1
        )

    with freezegun.freeze_time("2025-01-02T01:00:00Z"):
        run_procrastinate_jobs()
        assert (
            ProcrastinateJob.objects.filter(
                task_name=TASK_NAME,
                status="succeeded",
            ).count()
            == 1
        )


@pytest.mark.django_db(transaction=True)
def test_run_procrastinate_jobs_django_orm_modifications(run_procrastinate_jobs):
    my_test_task_plugin.defer(a=3, b=4)
    ProcrastinateJob.objects.update(
        scheduled_at=datetime.datetime(
            2100, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc
        )
    )

    assert (
        ProcrastinateJob.objects.filter(
            task_name=TASK_NAME,
            status="todo",
        ).count()
        == 1
    )

    # modify job scheduling using Django ORM
    ProcrastinateJob.objects.filter(task_name=TASK_NAME).update(
        scheduled_at=datetime.datetime(
            2020, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc
        )
    )

    run_procrastinate_jobs()

    # it should be picked up now because the scheduled_at is in the past
    assert (
        ProcrastinateJob.objects.filter(
            task_name=TASK_NAME,
            status="succeeded",
        ).count()
        == 1
    )
