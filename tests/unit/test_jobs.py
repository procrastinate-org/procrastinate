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
        job_store=job_store,
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


def test_job_defer(job_store):

    job = jobs.Job(
        queue="marsupilami",
        lock="sher",
        task_name="mytask",
        task_kwargs={"a": "b"},
        job_store=job_store,
    )

    id = job.defer(c=3)

    assert id == 0

    assert job_store.jobs == [
        jobs.Job(
            id=0,
            queue="marsupilami",
            task_name="mytask",
            lock="sher",
            task_kwargs={"a": "b", "c": 3},
            job_store=job_store,
        )
    ]


def test_job_scheduled_at_naive(job_store):
    with pytest.raises(ValueError):
        jobs.Job(
            id=12,
            queue="marsupilami",
            lock="sher",
            task_name="mytask",
            task_kwargs={"a": "b"},
            scheduled_at=pendulum.naive(2000, 1, 1),
            job_store=job_store,
        )
