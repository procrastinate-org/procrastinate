import pendulum
import pytest

from procrastinate import jobs


@pytest.mark.parametrize(
    "scheduled_at,context_scheduled_at",
    [
        (pendulum.datetime(2000, 1, 1, tz="Europe/Paris"), "2000-01-01T00:00:00+01:00"),
        (None, None),
    ],
)
def test_job_get_context(job_store, scheduled_at, context_scheduled_at):

    job = jobs.Job(
        id=12,
        queue="marsupilami",
        lock="sher",
        task_name="mytask",
        task_kwargs={"a": "b"},
        scheduled_at=scheduled_at,
        attempts=42,
    )

    assert job.get_context() == {
        "id": 12,
        "queue": "marsupilami",
        "lock": "sher",
        "task_name": "mytask",
        "task_kwargs": {"a": "b"},
        "scheduled_at": context_scheduled_at,
        "attempts": 42,
    }


def test_job_launcher_defer(job_store):

    job = jobs.Job(
        queue="marsupilami", lock="sher", task_name="mytask", task_kwargs={"a": "b"}
    )

    id = jobs.JobDeferrer(job=job, job_store=job_store).defer(c=3)

    assert id == 1

    assert job_store.jobs == {
        1: {
            "args": {"a": "b", "c": 3},
            "attempts": 0,
            "id": 1,
            "lock": "sher",
            "queue_name": "marsupilami",
            "scheduled_at": None,
            "started_at": None,
            "status": "todo",
            "task_name": "mytask",
        }
    }


@pytest.mark.asyncio
async def test_job_deferrer_defer_async(async_job_store):

    job = jobs.Job(
        queue="marsupilami", lock="sher", task_name="mytask", task_kwargs={"a": "b"}
    )

    deferrer = jobs.JobDeferrer(job=job, job_store=async_job_store)
    id = await deferrer.defer_async(c=3)

    assert id == 1

    assert async_job_store.jobs == {
        1: {
            "args": {"a": "b", "c": 3},
            "attempts": 0,
            "id": 1,
            "lock": "sher",
            "queue_name": "marsupilami",
            "scheduled_at": None,
            "started_at": None,
            "status": "todo",
            "task_name": "mytask",
        }
    }


def test_job_scheduled_at_naive(job_store):
    with pytest.raises(ValueError):
        jobs.Job(
            id=12,
            queue="marsupilami",
            lock="sher",
            task_name="mytask",
            task_kwargs={"a": "b"},
            scheduled_at=pendulum.naive(2000, 1, 1),
        )
