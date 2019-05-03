import pytest

from cabbage import jobs, testing


@pytest.fixture
def job_store():
    return testing.InMemoryJobStore()


def test_job_get_context(job_store):

    job = jobs.Job(
        id=12,
        queue="marsupilami",
        lock="sher",
        task_name="mytask",
        task_kwargs={"a": "b"},
        job_store=job_store,
    )

    assert job.get_context() == {
        "id": 12,
        "queue": "marsupilami",
        "lock": "sher",
        "task_name": "mytask",
        "task_kwargs": {"a": "b"},
    }


def test_job_defer(job_store):
    job_store.register_queue("marsupilami")

    job = jobs.Job(
        queue="marsupilami",
        lock="sher",
        task_name="mytask",
        task_kwargs={"a": "b"},
        job_store=job_store,
    )

    id = job.defer(c=3)

    assert id == 0

    assert job_store.jobs["marsupilami"] == [
        jobs.Job(
            id=0,
            queue="marsupilami",
            task_name="mytask",
            lock="sher",
            task_kwargs={"a": "b", "c": 3},
            job_store=job_store,
        )
    ]
