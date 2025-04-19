from __future__ import annotations

import datetime
import uuid

import pytest

from procrastinate import exceptions, jobs, manager, utils

from .. import conftest


@pytest.fixture
async def worker_id(job_manager):
    return await job_manager.register_worker()


async def test_manager_defer_job(job_manager, job_factory, connector):
    job = await job_manager.defer_job_async(
        job=job_factory(
            task_kwargs={"a": "b"},
            queue="marsupilami",
            task_name="bla",
            priority=5,
            lock="sher",
        )
    )

    assert job.id == 1

    assert connector.jobs == {
        1: {
            "args": {"a": "b"},
            "attempts": 0,
            "id": 1,
            "lock": "sher",
            "queueing_lock": None,
            "queue_name": "marsupilami",
            "priority": 5,
            "scheduled_at": None,
            "status": "todo",
            "task_name": "bla",
            "abort_requested": False,
            "worker_id": None,
        }
    }


async def test_manager_defer_job_no_lock(job_manager, job_factory, connector):
    await job_manager.defer_job_async(job=job_factory())

    assert uuid.UUID(connector.jobs[1]["lock"])


async def test_manager_defer_job_connector_exception(
    mocker, job_manager, job_factory, connector
):
    connector.execute_query_one_async = mocker.Mock(
        side_effect=exceptions.ConnectorException
    )

    with pytest.raises(exceptions.ConnectorException):
        await job_manager.defer_job_async(job=job_factory(task_kwargs={"a": "b"}))


async def test_manager_defer_job_unique_violation_exception(
    mocker, job_manager, job_factory, connector
):
    connector.execute_query_one_async = mocker.Mock(
        side_effect=exceptions.UniqueViolation(
            constraint_name="procrastinate_jobs_queueing_lock_idx_v1"
        )
    )

    with pytest.raises(exceptions.AlreadyEnqueued):
        await job_manager.defer_job_async(job=job_factory(task_kwargs={"a": "b"}))


async def test_manager_defer_job_unique_violation_exception_other_constraint(
    mocker, job_manager, job_factory, connector
):
    connector.execute_query_one_async = mocker.Mock(
        side_effect=exceptions.UniqueViolation(constraint_name="some_other_constraint")
    )

    with pytest.raises(exceptions.ConnectorException):
        await job_manager.defer_job_async(job=job_factory(task_kwargs={"a": "b"}))


async def test_manager_defer_job_unique_violation_exception_sync(
    mocker, job_manager, job_factory, connector
):
    connector.execute_query_one = mocker.Mock(
        side_effect=exceptions.UniqueViolation(
            constraint_name="procrastinate_jobs_queueing_lock_idx_v1"
        )
    )

    with pytest.raises(exceptions.AlreadyEnqueued):
        job_manager.defer_job(job=job_factory(task_kwargs={"a": "b"}))


async def test_manager_defer_job_unique_violation_exception_other_constraint_sync(
    mocker, job_manager, job_factory, connector
):
    connector.execute_query_one = mocker.Mock(
        side_effect=exceptions.UniqueViolation(constraint_name="some_other_constraint")
    )

    with pytest.raises(exceptions.ConnectorException):
        job_manager.defer_job(job=job_factory(task_kwargs={"a": "b"}))


async def test_fetch_job_no_suitable_job(job_manager, worker_id):
    assert await job_manager.fetch_job(queues=None, worker_id=worker_id) is None


async def test_fetch_job(job_manager, job_factory, worker_id):
    job = job_factory(id=None)
    await job_manager.defer_job_async(job=job)
    expected_job = job.evolve(id=1, status="doing", worker_id=worker_id)
    assert await job_manager.fetch_job(queues=None, worker_id=worker_id) == expected_job


async def test_get_stalled_jobs_by_started_not_stalled(job_manager, job_factory):
    job = job_factory(id=1)
    await job_manager.defer_job_async(job=job)
    with pytest.warns(DeprecationWarning, match=".*nb_seconds.*"):
        assert await job_manager.get_stalled_jobs(nb_seconds=1000) == []


async def test_get_stalled_jobs_by_started_stalled(
    job_manager, job_factory, connector, worker_id
):
    job = job_factory()
    await job_manager.defer_job_async(job=job)
    await job_manager.fetch_job(queues=None, worker_id=worker_id)
    connector.events[1][-1]["at"] = conftest.aware_datetime(2000, 1, 1)
    expected_job = job.evolve(id=1, status="doing", worker_id=worker_id)
    with pytest.warns(DeprecationWarning, match=".*nb_seconds.*"):
        assert await job_manager.get_stalled_jobs(nb_seconds=1000) == [expected_job]


async def test_get_stalled_jobs_by_heartbeat_not_stalled(job_manager, job_factory):
    job = job_factory(id=1)
    await job_manager.defer_job_async(job=job)
    assert await job_manager.get_stalled_jobs() == []


async def test_get_stalled_jobs_by_heartbeat_stalled(
    job_manager, job_factory, connector, worker_id
):
    job = job_factory()
    await job_manager.defer_job_async(job=job)
    await job_manager.fetch_job(queues=None, worker_id=worker_id)
    connector.workers = {1: conftest.aware_datetime(2000, 1, 1)}
    expected_job = job.evolve(id=1, status="doing", worker_id=worker_id)
    assert await job_manager.get_stalled_jobs() == [expected_job]


async def test_register_and_unregister_worker(job_manager, connector):
    then = utils.utcnow()
    assert connector.workers == {}
    worker_id = await job_manager.register_worker()
    assert worker_id is not None

    assert len(connector.workers) == 1
    assert worker_id in connector.workers
    assert then < connector.workers[worker_id] < utils.utcnow()

    await job_manager.unregister_worker(worker_id=1)

    assert connector.workers == {}


async def test_update_heartbeat(job_manager, connector, worker_id):
    first_heartbeat = connector.workers[worker_id]

    await job_manager.update_heartbeat(worker_id=worker_id)

    assert len(connector.workers) == 1
    assert worker_id in connector.workers
    assert first_heartbeat < connector.workers[worker_id] < utils.utcnow()


async def test_prune_stalled_workers(job_manager, connector, worker_id):
    assert len(connector.workers) == 1

    pruned_workers = await job_manager.prune_stalled_workers(
        seconds_since_heartbeat=1800
    )
    assert pruned_workers == []

    # We fake the heartbeat to be 35 minutes old
    heartbeat = connector.workers[worker_id]
    connector.workers[worker_id] = heartbeat - datetime.timedelta(minutes=35)

    pruned_workers = await job_manager.prune_stalled_workers(
        seconds_since_heartbeat=1800
    )
    assert pruned_workers == [worker_id]
    assert connector.workers == {}


@pytest.mark.parametrize(
    "include_failed, statuses",
    [(False, ["succeeded"]), (True, ["succeeded", "failed"])],
)
async def test_delete_old_jobs(
    job_manager, job_factory, connector, include_failed, statuses, mocker
):
    await job_manager.delete_old_jobs(
        nb_hours=5, queue="marsupilami", include_failed=include_failed
    )
    assert connector.queries == [
        (
            "delete_old_jobs",
            {"nb_hours": 5, "queue": "marsupilami", "statuses": statuses},
        )
    ]


async def test_finish_job(job_manager, job_factory, connector):
    job = job_factory(id=1)
    await job_manager.defer_job_async(job=job)

    await job_manager.finish_job(
        job=job, status=jobs.Status.SUCCEEDED, delete_job=False
    )
    assert connector.queries[-1] == (
        "finish_job",
        {"job_id": 1, "status": "succeeded", "delete_job": False},
    )


async def test_finish_job_with_deletion(job_manager, job_factory, connector):
    job = job_factory(id=1)
    await job_manager.defer_job_async(job=job)

    await job_manager.finish_job(job=job, status=jobs.Status.SUCCEEDED, delete_job=True)
    assert connector.queries[-1] == (
        "finish_job",
        {"job_id": 1, "status": "succeeded", "delete_job": True},
    )
    assert 1 not in connector.jobs


def test_cancel_todo_job(job_manager, job_factory, connector):
    job = job_factory(id=1)
    job_manager.defer_job(job=job)

    cancelled = job_manager.cancel_job_by_id(job_id=1)
    assert cancelled
    assert connector.queries[-1] == (
        "cancel_job",
        {"job_id": 1, "abort": False, "delete_job": False},
    )
    assert connector.jobs[1]["status"] == "cancelled"


def test_delete_cancelled_todo_job(job_manager, job_factory, connector):
    job = job_factory(id=1)
    job_manager.defer_job(job=job)

    cancelled = job_manager.cancel_job_by_id(job_id=1, delete_job=True)
    assert cancelled
    assert connector.queries[-1] == (
        "cancel_job",
        {"job_id": 1, "abort": False, "delete_job": True},
    )
    assert len(connector.jobs) == 0


async def test_cancel_todo_job_async(job_manager, job_factory, connector):
    job = job_factory(id=1)
    await job_manager.defer_job_async(job=job)

    cancelled = await job_manager.cancel_job_by_id_async(job_id=1)
    assert cancelled
    assert connector.queries[-1] == (
        "cancel_job",
        {"job_id": 1, "abort": False, "delete_job": False},
    )
    assert connector.jobs[1]["status"] == "cancelled"


async def test_delete_cancelled_todo_job_async(job_manager, job_factory, connector):
    job = job_factory(id=1)
    await job_manager.defer_job_async(job=job)

    cancelled = await job_manager.cancel_job_by_id_async(job_id=1, delete_job=True)
    assert cancelled
    assert connector.queries[-1] == (
        "cancel_job",
        {"job_id": 1, "abort": False, "delete_job": True},
    )
    assert len(connector.jobs) == 0


async def test_cancel_doing_job(job_manager, job_factory, connector, worker_id):
    job = job_factory(id=1)
    await job_manager.defer_job_async(job=job)
    await job_manager.fetch_job(queues=None, worker_id=worker_id)

    cancelled = await job_manager.cancel_job_by_id_async(job_id=1)
    assert not cancelled
    assert connector.queries[-1] == (
        "cancel_job",
        {"job_id": 1, "abort": False, "delete_job": False},
    )
    assert connector.jobs[1]["status"] == "doing"


async def test_abort_doing_job(job_manager, job_factory, connector, worker_id):
    job = job_factory(id=1)
    await job_manager.defer_job_async(job=job)
    await job_manager.fetch_job(queues=None, worker_id=worker_id)

    cancelled = await job_manager.cancel_job_by_id_async(job_id=1, abort=True)
    assert cancelled
    assert connector.queries[-1] == (
        "cancel_job",
        {"job_id": 1, "abort": True, "delete_job": False},
    )
    assert connector.jobs[1]["status"] == "doing"
    assert connector.jobs[1]["abort_requested"] is True


def test_get_job_status(job_manager, job_factory, connector):
    job = job_factory(id=1)
    job_manager.defer_job(job=job)

    assert job_manager.get_job_status(job_id=1) == jobs.Status.TODO


async def test_get_job_status_async(job_manager, job_factory, connector, worker_id):
    job = job_factory(id=1)
    await job_manager.defer_job_async(job=job)

    assert await job_manager.get_job_status_async(job_id=1) == jobs.Status.TODO

    await job_manager.fetch_job(queues=None, worker_id=worker_id)
    assert await job_manager.get_job_status_async(job_id=1) == jobs.Status.DOING


async def test_retry_job(job_manager, job_factory, connector):
    job = job_factory(id=1)
    await job_manager.defer_job_async(job=job)
    retry_at = conftest.aware_datetime(2000, 1, 1)

    await job_manager.retry_job(
        job=job, retry_at=retry_at, priority=7, queue="some_queue", lock="some_lock"
    )
    assert connector.queries[-1] == (
        "retry_job",
        {
            "job_id": 1,
            "retry_at": retry_at,
            "new_priority": 7,
            "new_queue_name": "some_queue",
            "new_lock": "some_lock",
        },
    )


@pytest.mark.parametrize(
    "queues, channels",
    [
        (None, ["procrastinate_any_queue_v1"]),
        (["a", "b"], ["procrastinate_queue_v1#a", "procrastinate_queue_v1#b"]),
    ],
)
async def test_listen_for_jobs(job_manager, connector, mocker, queues, channels):
    on_notification = mocker.Mock()

    await job_manager.listen_for_jobs(queues=queues, on_notification=on_notification)
    assert connector.on_notification
    assert connector.notify_channels == channels


@pytest.fixture
def configure(app):
    @app.task
    def foo(timestamp: int):
        pass

    return foo.configure


async def test_defer_periodic_job(configure):
    deferrer = configure(task_kwargs={"timestamp": 1234567890})

    result = await deferrer.job_manager.defer_periodic_job(
        job=deferrer.job,
        periodic_id="",
        defer_timestamp=1234567890,
    )
    assert result == 1


async def test_defer_periodic_job_with_suffixes(configure):
    deferrer = configure(task_kwargs={"timestamp": 1234567890})

    result = [
        await deferrer.job_manager.defer_periodic_job(
            job=deferrer.job,
            periodic_id="1",
            defer_timestamp=1234567890,
        ),
        await deferrer.job_manager.defer_periodic_job(
            job=deferrer.job,
            periodic_id="2",
            defer_timestamp=1234567890,
        ),
    ]

    assert result == [1, 2]


async def test_defer_periodic_job_unique_violation(configure):
    deferrer1 = configure(
        queueing_lock="bla",
        task_kwargs={"timestamp": 1234567890},
    )
    deferrer2 = configure(
        queueing_lock="bla",
        task_kwargs={"timestamp": 1234567891},
    )

    await deferrer1.job_manager.defer_periodic_job(
        job=deferrer1.job,
        periodic_id="",
        defer_timestamp=1234567890,
    )
    with pytest.raises(exceptions.AlreadyEnqueued):
        await deferrer2.job_manager.defer_periodic_job(
            job=deferrer2.job,
            periodic_id="",
            defer_timestamp=1234567891,
        )


async def test_defer_periodic_job_wrong_timestamp(configure):
    deferrer = configure(
        queueing_lock="bla",
        task_kwargs={"timestamp": 1000000000},
    )

    with pytest.raises(exceptions.InvalidTimestamp):
        await deferrer.job_manager.defer_periodic_job(
            job=deferrer.job,
            periodic_id="",
            defer_timestamp=1234567890,
        )


def test_raise_already_enqueued_right_constraint(job_manager):
    class UniqueViolation(Exception):
        constraint_name = manager.QUEUEING_LOCK_CONSTRAINT

    with pytest.raises(exceptions.AlreadyEnqueued) as exc_info:
        job_manager._raise_already_enqueued(exc=UniqueViolation(), queueing_lock="foo")

    assert "queueing lock foo" in str(exc_info.value)


def test_raise_already_enqueued_wrong_constraint(job_manager):
    class UniqueViolation(Exception):
        constraint_name = "foo"

    with pytest.raises(UniqueViolation):
        job_manager._raise_already_enqueued(exc=UniqueViolation(), queueing_lock="foo")


@pytest.fixture
def dt():
    return datetime.datetime(2000, 1, 1, tzinfo=datetime.timezone.utc)


async def test_retry_job_by_id_async(job_manager, connector, job_factory, dt):
    job = await job_manager.defer_job_async(job=job_factory())

    await job_manager.retry_job_by_id_async(
        job_id=job.id, retry_at=dt, priority=7, queue="some_queue", lock="some_lock"
    )

    assert connector.queries[-1] == (
        "retry_job",
        {
            "job_id": 1,
            "retry_at": dt,
            "new_priority": 7,
            "new_queue_name": "some_queue",
            "new_lock": "some_lock",
        },
    )


def test_retry_job_by_id(job_manager, connector, job_factory, dt):
    job = job_manager.defer_job(job=job_factory())

    job_manager.retry_job_by_id(
        job_id=job.id, retry_at=dt, priority=7, queue="some_queue", lock="some_lock"
    )

    assert connector.queries[-1] == (
        "retry_job",
        {
            "job_id": 1,
            "retry_at": dt,
            "new_priority": 7,
            "new_queue_name": "some_queue",
            "new_lock": "some_lock",
        },
    )


async def test_retry_failed_job_by_id_async(job_manager, connector, job_factory, dt):
    job = await job_manager.defer_job_async(job=job_factory())

    await job_manager.retry_failed_job_by_id_async(
        job_id=job.id, priority=7, queue="some_queue", lock="some_lock"
    )

    assert connector.queries[-1] == (
        "retry_failed_job",
        {
            "job_id": 1,
            "new_priority": 7,
            "new_queue_name": "some_queue",
            "new_lock": "some_lock",
        },
    )


def test_retry_failed_job_by_id(job_manager, connector, job_factory, dt):
    job = job_manager.defer_job(job=job_factory())

    job_manager.retry_failed_job_by_id(
        job_id=job.id, priority=7, queue="some_queue", lock="some_lock"
    )

    assert connector.queries[-1] == (
        "retry_failed_job",
        {
            "job_id": 1,
            "new_priority": 7,
            "new_queue_name": "some_queue",
            "new_lock": "some_lock",
        },
    )


async def test_list_jobs_async(job_manager, job_factory):
    job = await job_manager.defer_job_async(job=job_factory())

    assert await job_manager.list_jobs_async() == [job]


def test_list_jobs(job_manager, job_factory):
    job = job_manager.defer_job(job=job_factory())

    assert job_manager.list_jobs() == [job]


async def test_list_queues_async(job_manager, job_factory):
    await job_manager.defer_job_async(job=job_factory(queue="foo"))

    assert await job_manager.list_queues_async() == [
        {
            "name": "foo",
            "jobs_count": 1,
            "todo": 1,
            "doing": 0,
            "succeeded": 0,
            "failed": 0,
            "cancelled": 0,
            "aborted": 0,
        }
    ]


def test_list_queues_(job_manager, job_factory):
    job_manager.defer_job(job=job_factory(queue="foo"))

    assert job_manager.list_queues() == [
        {
            "name": "foo",
            "jobs_count": 1,
            "todo": 1,
            "doing": 0,
            "succeeded": 0,
            "failed": 0,
            "cancelled": 0,
            "aborted": 0,
        }
    ]


async def test_list_tasks_async(job_manager, job_factory):
    await job_manager.defer_job_async(job=job_factory(task_name="foo"))

    assert await job_manager.list_tasks_async() == [
        {
            "name": "foo",
            "jobs_count": 1,
            "todo": 1,
            "doing": 0,
            "succeeded": 0,
            "failed": 0,
            "cancelled": 0,
            "aborted": 0,
        }
    ]


def test_list_tasks(job_manager, job_factory):
    job_manager.defer_job(job=job_factory(task_name="foo"))

    assert job_manager.list_tasks() == [
        {
            "name": "foo",
            "jobs_count": 1,
            "todo": 1,
            "doing": 0,
            "succeeded": 0,
            "failed": 0,
            "cancelled": 0,
            "aborted": 0,
        }
    ]


async def test_list_locks_async(job_manager, job_factory):
    await job_manager.defer_job_async(job=job_factory(lock="foo"))

    assert await job_manager.list_locks_async() == [
        {
            "name": "foo",
            "jobs_count": 1,
            "todo": 1,
            "doing": 0,
            "succeeded": 0,
            "failed": 0,
            "cancelled": 0,
            "aborted": 0,
        }
    ]


def test_list_locks(job_manager, job_factory):
    job_manager.defer_job(job=job_factory(lock="foo"))

    assert job_manager.list_locks() == [
        {
            "name": "foo",
            "jobs_count": 1,
            "todo": 1,
            "doing": 0,
            "succeeded": 0,
            "failed": 0,
            "cancelled": 0,
            "aborted": 0,
        }
    ]


async def test_check_connection_async(job_manager, connector):
    assert await job_manager.check_connection_async() is True
    assert connector.queries == [("check_connection", {})]


def test_check_connection(job_manager, connector):
    assert job_manager.check_connection() is True
    assert connector.queries == [("check_connection", {})]
