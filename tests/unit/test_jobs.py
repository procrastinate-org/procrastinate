from __future__ import annotations

import datetime
import json

import pytest

from procrastinate import jobs

from .. import conftest


@pytest.mark.parametrize(
    "scheduled_at,context_scheduled_at",
    [
        (conftest.aware_datetime(2000, 1, 1, tz_offset=1), "2000-01-01T00:00:00+01:00"),
        (None, None),
    ],
)
def test_job_get_context(job_factory, scheduled_at, context_scheduled_at):
    job = job_factory(
        id=12,
        status="doing",
        queue="marsupilami",
        priority=5,
        lock="sher",
        queueing_lock="houba",
        task_name="mytask",
        task_kwargs={"a": "b"},
        scheduled_at=scheduled_at,
        attempts=42,
    )

    assert job.log_context() == {
        "id": 12,
        "status": "doing",
        "queue": "marsupilami",
        "priority": 5,
        "lock": "sher",
        "queueing_lock": "houba",
        "task_name": "mytask",
        "task_kwargs": {"a": "b"},
        "scheduled_at": context_scheduled_at,
        "attempts": 42,
        "call_string": "mytask[12](a='b')",
        "abort_requested": False,
        "worker_id": None,
    }


def test_log_context_does_not_grow_infinitely(job_factory):
    large_arg_len = 10**5
    job = job_factory(
        task_kwargs={"large_arg": "a" * large_arg_len},
    )

    assert len(json.dumps(job.log_context())) < large_arg_len


def test_job_evolve(job_factory):
    job = job_factory(id=12, task_name="mytask", lock="sher", queue="marsupilami")
    expected = job_factory(id=13, task_name="mytask", lock="bu", queue="marsupilami")

    assert job.evolve(id=13, lock="bu") == expected


async def test_job_deferrer_defer_async(job_factory, job_manager, connector):
    job = job_factory(
        queue="marsupilami",
        lock="sher",
        priority=5,
        queueing_lock="houba",
        task_name="mytask",
        task_kwargs={"a": "b"},
    )

    deferrer = jobs.JobDeferrer(job=job, job_manager=job_manager)
    id = await deferrer.defer_async(c=3)

    assert id == 1

    assert connector.jobs == {
        1: {
            "args": {"a": "b", "c": 3},
            "attempts": 0,
            "id": 1,
            "lock": "sher",
            "queueing_lock": "houba",
            "queue_name": "marsupilami",
            "priority": 5,
            "scheduled_at": None,
            "status": "todo",
            "task_name": "mytask",
            "abort_requested": False,
            "worker_id": None,
        }
    }


def test_job_scheduled_at_naive(job_factory):
    with pytest.raises(ValueError):
        job_factory(scheduled_at=datetime.datetime(2000, 1, 1))


def test_call_string(job_factory):
    job = job_factory(id=12, task_name="mytask", task_kwargs={"a": "b"})

    assert job.call_string == "mytask[12](a='b')"
