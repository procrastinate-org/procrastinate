import uuid

import pytest

from procrastinate import exceptions, jobs

from .. import conftest

pytestmark = pytest.mark.asyncio


async def test_store_defer_job(job_store, job_factory, connector):
    job_row = await job_store.defer_job_async(
        job=job_factory(
            task_kwargs={"a": "b"}, queue="marsupilami", task_name="bla", lock="sher"
        )
    )

    assert job_row == 1

    assert connector.jobs == {
        1: {
            "args": {"a": "b"},
            "attempts": 0,
            "id": 1,
            "lock": "sher",
            "queueing_lock": None,
            "queue_name": "marsupilami",
            "scheduled_at": None,
            "status": "todo",
            "task_name": "bla",
        }
    }


async def test_store_defer_job_no_lock(job_store, job_factory, connector):
    await job_store.defer_job_async(job=job_factory())

    assert uuid.UUID(connector.jobs[1]["lock"])


async def test_store_defer_job_connector_exception(
    mocker, job_store, job_factory, connector
):
    connector.execute_query_one_async = mocker.Mock(
        side_effect=exceptions.ConnectorException
    )

    with pytest.raises(exceptions.ConnectorException):
        await job_store.defer_job_async(job=job_factory(task_kwargs={"a": "b"}))


async def test_store_defer_job_unique_violation_exception(
    mocker, job_store, job_factory, connector
):
    connector.execute_query_one_async = mocker.Mock(
        side_effect=exceptions.UniqueViolation(
            constraint_name="procrastinate_jobs_queueing_lock_idx"
        )
    )

    with pytest.raises(exceptions.AlreadyEnqueued):
        await job_store.defer_job_async(job=job_factory(task_kwargs={"a": "b"}))


async def test_store_defer_job_unique_violation_exception_other_constraint(
    mocker, job_store, job_factory, connector
):
    connector.execute_query_one_async = mocker.Mock(
        side_effect=exceptions.UniqueViolation(constraint_name="some_other_constraint")
    )

    with pytest.raises(exceptions.ConnectorException):
        await job_store.defer_job_async(job=job_factory(task_kwargs={"a": "b"}))


async def test_fetch_job_no_suitable_job(job_store):
    assert await job_store.fetch_job(queues=None) is None


async def test_fetch_job(job_store, job_factory):
    job = job_factory(id=1)
    await job_store.defer_job_async(job=job)
    assert await job_store.fetch_job(queues=None) == job


async def test_get_stalled_jobs_not_stalled(job_store, job_factory):
    job = job_factory(id=1)
    await job_store.defer_job_async(job=job)
    assert await job_store.get_stalled_jobs(nb_seconds=1000) == []


async def test_get_stalled_jobs_stalled(job_store, job_factory, connector):
    job = job_factory(id=1)
    await job_store.defer_job_async(job=job)
    await job_store.fetch_job(queues=None)
    connector.events[1][-1]["at"] = conftest.aware_datetime(2000, 1, 1)
    assert await job_store.get_stalled_jobs(nb_seconds=1000) == [job]


@pytest.mark.parametrize(
    "include_error, statuses",
    [(False, ("succeeded",)), (True, ("succeeded", "failed"))],
)
async def test_delete_old_jobs(
    job_store, job_factory, connector, include_error, statuses, mocker
):

    await job_store.delete_old_jobs(
        nb_hours=5, queue="marsupilami", include_error=include_error
    )
    assert connector.queries == [
        (
            "delete_old_jobs",
            {"nb_hours": 5, "queue": "marsupilami", "statuses": statuses},
        )
    ]


async def test_finish_job(job_store, job_factory, connector):
    job = job_factory(id=1)
    await job_store.defer_job_async(job=job)
    retry_at = conftest.aware_datetime(2000, 1, 1)

    await job_store.finish_job(job=job, status=jobs.Status.TODO, scheduled_at=retry_at)
    assert connector.queries[-1] == (
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
async def test_listen_for_jobs(job_store, connector, mocker, queues, channels):
    event = mocker.Mock()

    await job_store.listen_for_jobs(queues=queues, event=event)
    assert connector.notify_event is event
    assert connector.notify_channels == channels


async def test_defer_periodic_job(job_store, connector, app):
    @app.task
    def foo(timestamp):
        pass

    result = await job_store.defer_periodic_job(foo, 1234567890)
    assert result == 1
