import pendulum
import pytest

from procrastinate import jobs


def test_store_defer(job_store, job_factory):
    job_row = job_store.defer_job(job=job_factory(task_kwargs={"a": "b"}))

    assert job_row == 1

    assert job_store.jobs == {
        1: {
            "args": {"a": "b"},
            "attempts": 0,
            "id": 1,
            "lock": None,
            "queue_name": "queue",
            "scheduled_at": None,
            "started_at": None,
            "status": "todo",
            "task_name": "bla",
        }
    }


def test_fetch_job_no_suitable_job(job_store):
    assert job_store.fetch_job(queues=None) is None


def test_fetch_job(job_store, job_factory):
    job = job_factory(id=1)
    job_store.defer_job(job=job)
    assert job_store.fetch_job(queues=None) == job


def test_get_stalled_jobs_not_stalled(job_store, job_factory):
    job = job_factory(id=1)
    job_store.defer_job(job=job)
    assert list(job_store.get_stalled_jobs(nb_seconds=1000)) == []


def test_get_stalled_jobs_stalled(job_store, job_factory):
    job = job_factory(id=1)
    job_store.defer_job(job=job)
    job_store.fetch_job(queues=None)
    job_store.jobs[1]["started_at"] = pendulum.datetime(2000, 1, 1)
    assert list(job_store.get_stalled_jobs(nb_seconds=1000)) == [job]


@pytest.mark.parametrize(
    "include_error, statuses",
    [(False, ("succeeded",)), (True, ("succeeded", "failed"))],
)
async def test_delete_old_jobs(job_store, job_factory, include_error, statuses, mocker):

    await job_store.delete_old_jobs(
        nb_hours=5, queue="marsupilami", include_error=include_error
    )
    assert job_store.queries == [
        (
            "delete_old_jobs",
            {"nb_hours": 5, "queue": "marsupilami", "statuses": statuses},
        )
    ]


async def test_finish_job(job_store, job_factory):
    job = job_factory(id=1)
    await job_store.defer_job(job=job)
    retry_at = pendulum.datetime(2000, 1, 1)

    await job_store.finish_job(job=job, status=jobs.Status.TODO, scheduled_at=retry_at)
    assert job_store.queries[-1] == (
        "finish_job",
        {"job_id": 1, "scheduled_at": retry_at, "status": "todo"},
    )


@pytest.mark.parametrize(
    "queues, channels",
    [
        (None, ["procrastinate_any_queue"]),
        (["a", "b"], ["procrastinate_queue#a", "procrastinate_queue#b"]),
    ],
)
async def test_listen_for_jobs(job_store, mocker, queues, channels):
    await job_store.listen_for_jobs(queues)
    assert job_store.queries == [("listen_for_jobs", channel) for channel in channels]
