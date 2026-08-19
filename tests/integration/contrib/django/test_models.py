from __future__ import annotations

import asyncio
import datetime

import pytest

import procrastinate
import procrastinate.contrib.django
import procrastinate.contrib.django.exceptions
from procrastinate import jobs as jobs_module
from procrastinate.contrib.django import models


def test_procrastinate_job(db):
    job_id = procrastinate.contrib.django.app.configure_task("test_task").defer(
        a=1, b=2
    )
    job = models.ProcrastinateJob.objects.values().get(task_name="test_task")
    assert job == {
        "id": job_id,
        "queue_name": "default",
        "task_name": "test_task",
        "priority": 0,
        "lock": None,
        "args": {"a": 1, "b": 2},
        "status": "todo",
        "scheduled_at": None,
        "attempts": 0,
        "queueing_lock": None,
        "abort_requested": False,
        "worker_id": None,
    }


def test_procrastinate_job__property(db):
    job = models.ProcrastinateJob(
        id=1,
        queue_name="foo",
        task_name="test_task",
        priority=0,
        lock="bar",
        args={"a": 1, "b": 2},
        status="todo",
        scheduled_at=datetime.datetime(2021, 1, 1, tzinfo=datetime.timezone.utc),
        attempts=0,
        queueing_lock="baz",
        abort_requested=False,
        worker_id=None,
    )
    assert job.procrastinate_job == jobs_module.Job(
        id=1,
        queue="foo",
        task_name="test_task",
        task_kwargs={"a": 1, "b": 2},
        priority=0,
        lock="bar",
        status="todo",
        scheduled_at=datetime.datetime(2021, 1, 1, tzinfo=datetime.timezone.utc),
        attempts=0,
        queueing_lock="baz",
    )


def test_procrastinate_job__no_create(db):
    with pytest.raises(procrastinate.contrib.django.exceptions.ReadOnlyModel):
        models.ProcrastinateJob.objects.create(task_name="test_task")


def test_procrastinate_job__create__with_setting(db, settings):
    settings.PROCRASTINATE_READONLY_MODELS = False
    assert models.ProcrastinateJob.objects.create(
        task_name="test_task",
        queue_name="foo",
        priority=0,
        lock="bar",
        args={"a": 1, "b": 2},
        status="todo",
        scheduled_at=datetime.datetime.now(datetime.timezone.utc),
        attempts=0,
        queueing_lock="baz",
        abort_requested=False,
    )


def test_procrastinate_job__no_save(db):
    with pytest.raises(procrastinate.contrib.django.exceptions.ReadOnlyModel):
        models.ProcrastinateJob().save()


def test_procrastinate_job__no_delete(db):
    with pytest.raises(procrastinate.contrib.django.exceptions.ReadOnlyModel):
        models.ProcrastinateJob().delete()


def test_procrastinate_event(db):
    job_id = procrastinate.contrib.django.app.configure_task("test_task").defer(
        a=1, b=2
    )
    now = datetime.datetime.now(datetime.timezone.utc)
    one_sec = datetime.timedelta(seconds=1)
    event = models.ProcrastinateEvent.objects.values().get(job_id=job_id)
    at = event.pop("at")
    event.pop("id")
    assert event == {
        "job_id": job_id,
        "type": "deferred",
    }
    assert now - one_sec < at < now + one_sec


async def test_procrastinate_periodic_defers(db):
    @procrastinate.contrib.django.app.periodic(cron="* * * * *", periodic_id="bar")
    @procrastinate.contrib.django.app.task(name="foo")
    def my_task(timestamp):
        pass

    async def list_periodic_defers():
        return [
            element
            async for element in models.ProcrastinatePeriodicDefer.objects.values().all()
        ]

    async def wait_for_periodic_defer():
        while not await list_periodic_defers():
            await asyncio.sleep(0.01)

    django_app = procrastinate.contrib.django.app
    with django_app.replace_connector(
        django_app.connector.get_worker_connector()
    ) as app:
        async with app.open_async():
            worker = asyncio.create_task(app.run_worker_async())
            try:
                # Run the worker until the deferrer has actually written its row.
                # Giving it a fixed budget instead makes the test depend on worker
                # startup fitting in that window, which it doesn't on a loaded runner.
                await asyncio.wait_for(wait_for_periodic_defer(), timeout=5)
            finally:
                worker.cancel()
                try:
                    await worker
                except asyncio.CancelledError:
                    pass

    periodic_defers = await list_periodic_defers()

    assert periodic_defers[-1]["periodic_id"] == "bar"
    assert periodic_defers[-1]["task_name"] == "foo"
