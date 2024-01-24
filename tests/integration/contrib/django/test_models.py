from __future__ import annotations

import datetime

import pytest

import procrastinate
import procrastinate.contrib.django
import procrastinate.contrib.django.exceptions
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
        "lock": None,
        "args": {"a": 1, "b": 2},
        "status": "todo",
        "scheduled_at": None,
        "attempts": 0,
        "queueing_lock": None,
    }


def test_procrastinate_job__no_create(db):
    with pytest.raises(procrastinate.contrib.django.exceptions.ReadOnlyModel):
        models.ProcrastinateJob.objects.create(task_name="test_task")


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
    assert event == {
        "id": 2,
        "job_id": 2,
        "type": "deferred",
    }
    assert now - one_sec < at < now + one_sec
