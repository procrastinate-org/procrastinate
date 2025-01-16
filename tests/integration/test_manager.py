from __future__ import annotations

import datetime
import functools

import pytest

from procrastinate import exceptions, jobs, manager

from .. import conftest


@pytest.fixture
def pg_job_manager(psycopg_connector):
    return manager.JobManager(connector=psycopg_connector)


@pytest.fixture
def get_all(psycopg_connector):
    async def f(table, *fields):
        return await psycopg_connector.execute_query_all_async(
            f"SELECT {', '.join(fields)} FROM {table}"
        )

    return f


@pytest.fixture
def deferred_job_factory(deferred_job_factory, pg_job_manager):
    return functools.partial(deferred_job_factory, job_manager=pg_job_manager)


@pytest.fixture
def fetched_job_factory(deferred_job_factory, pg_job_manager):
    async def factory(**kwargs):
        job = await deferred_job_factory(**kwargs)
        fetched_job = await pg_job_manager.fetch_job(queues=None)
        # to make sure we do fetch the job we just deferred
        assert fetched_job.id == job.id
        return fetched_job

    return factory


@pytest.mark.parametrize(
    "job_kwargs, fetch_queues",
    [
        ({"queue": "queue_a"}, None),
        ({"queue": "queue_a"}, ["queue_a"]),
        ({"scheduled_at": conftest.aware_datetime(2000, 1, 1)}, None),
    ],
)
async def test_fetch_job(
    pg_job_manager,
    deferred_job_factory,
    job_kwargs,
    fetch_queues,
):
    # Now add the job we're testing
    job = await deferred_job_factory(**job_kwargs)

    expected_job = job.evolve(status="doing")
    assert await pg_job_manager.fetch_job(queues=fetch_queues) == expected_job


async def test_fetch_job_not_fetching_started_job(pg_job_manager, fetched_job_factory):
    # Add a first started job
    await fetched_job_factory()

    assert await pg_job_manager.fetch_job(queues=None) is None


async def test_fetch_job_not_fetching_locked_job(
    pg_job_manager, deferred_job_factory, fetched_job_factory
):
    await fetched_job_factory(lock="lock_1")
    await deferred_job_factory(lock="lock_1")

    assert await pg_job_manager.fetch_job(queues=None) is None


async def test_fetch_job_respect_lock_aborting_job(
    pg_job_manager, deferred_job_factory, fetched_job_factory
):
    job = await fetched_job_factory(lock="lock_1")
    await deferred_job_factory(lock="lock_1")

    await pg_job_manager.cancel_job_by_id_async(job.id, abort=True)
    assert await pg_job_manager.fetch_job(queues=None) is None


async def test_fetch_job_spacial_case_none_lock(
    pg_job_manager, deferred_job_factory, fetched_job_factory
):
    await fetched_job_factory(lock=None)
    job = await deferred_job_factory(lock=None)

    assert (await pg_job_manager.fetch_job(queues=None)).id == job.id


@pytest.mark.parametrize(
    "job_kwargs, fetch_queues",
    [
        # We won't see this one because of the queue
        ({"queue": "queue_b"}, ["queue_a"]),
        # We won't see this one because of the scheduled date
        ({"scheduled_at": conftest.aware_datetime(2100, 1, 1)}, None),
    ],
)
async def test_fetch_job_no_result(
    pg_job_manager, deferred_job_factory, job_kwargs, fetch_queues
):
    await deferred_job_factory(**job_kwargs)

    assert await pg_job_manager.fetch_job(queues=fetch_queues) is None


@pytest.mark.parametrize(
    "filter_args",
    [
        {"nb_seconds": 1800},
        {"nb_seconds": 1800, "queue": "queue_a"},
        {"nb_seconds": 1800, "task_name": "task_1"},
    ],
)
async def test_get_stalled_jobs_yes(
    pg_job_manager, fetched_job_factory, psycopg_connector, filter_args
):
    job = await fetched_job_factory(queue="queue_a", task_name="task_1")

    # We fake its started event timestamp
    await psycopg_connector.execute_query_async(
        f"UPDATE procrastinate_events SET at=at - INTERVAL '35 minutes'"
        f"WHERE job_id={job.id}"
    )

    result = await pg_job_manager.get_stalled_jobs(**filter_args)
    assert result == [job]


@pytest.mark.parametrize(
    "filter_args",
    [
        {"nb_seconds": 3600},
        {"nb_seconds": 1800, "queue": "queue_b"},
        {"nb_seconds": 1800, "task_name": "task_2"},
    ],
)
async def test_get_stalled_jobs_no(
    pg_job_manager, fetched_job_factory, psycopg_connector, filter_args
):
    job = await fetched_job_factory(queue="queue_a", task_name="task_1")

    # We fake its started event timestamp
    await psycopg_connector.execute_query_async(
        f"UPDATE procrastinate_events SET at=at - INTERVAL '35 minutes'"
        f"WHERE job_id={job.id}"
    )

    result = await pg_job_manager.get_stalled_jobs(**filter_args)
    assert result == []


async def test_delete_old_jobs_job_todo(
    get_all,
    pg_job_manager,
    psycopg_connector,
    deferred_job_factory,
):
    job = await deferred_job_factory(queue="queue_a")

    # We fake its started event timestamp
    await psycopg_connector.execute_query_async(
        f"UPDATE procrastinate_events SET at=at - INTERVAL '2 hours'"
        f"WHERE job_id={job.id}"
    )

    await pg_job_manager.delete_old_jobs(nb_hours=0)
    assert len(await get_all("procrastinate_jobs", "id")) == 1


async def test_delete_old_jobs_job_doing(
    get_all,
    pg_job_manager,
    psycopg_connector,
    fetched_job_factory,
):
    job = await fetched_job_factory(queue="queue_a")

    # We fake its started event timestamp
    await psycopg_connector.execute_query_async(
        f"UPDATE procrastinate_events SET at=at - INTERVAL '2 hours'"
        f"WHERE job_id={job.id}"
    )

    await pg_job_manager.delete_old_jobs(nb_hours=0)
    assert len(await get_all("procrastinate_jobs", "id")) == 1


@pytest.mark.parametrize(
    "status, nb_hours, queue, include_failed, expected_job_count",
    [
        # nb_hours
        (jobs.Status.SUCCEEDED, 1, None, False, 0),
        (jobs.Status.SUCCEEDED, 3, None, False, 1),
        # queue
        (jobs.Status.SUCCEEDED, 1, "queue_a", False, 0),
        (jobs.Status.SUCCEEDED, 3, "queue_a", False, 1),
        (jobs.Status.SUCCEEDED, 1, "queue_b", False, 1),
        (jobs.Status.SUCCEEDED, 1, "queue_b", False, 1),
        # include_failed
        (jobs.Status.FAILED, 1, None, False, 1),
        (jobs.Status.FAILED, 1, None, True, 0),
    ],
)
async def test_delete_old_jobs_parameters(
    get_all,
    pg_job_manager,
    psycopg_connector,
    status,
    nb_hours,
    queue,
    include_failed,
    expected_job_count,
    fetched_job_factory,
):
    job = await fetched_job_factory(queue="queue_a")

    # We finish the job
    await pg_job_manager.finish_job(job, status=status, delete_job=False)

    # We fake its started event timestamp
    await psycopg_connector.execute_query_async(
        f"UPDATE procrastinate_events SET at=at - INTERVAL '2 hours'"
        f"WHERE job_id={job.id}"
    )

    await pg_job_manager.delete_old_jobs(
        nb_hours=nb_hours, queue=queue, include_failed=include_failed
    )
    jobs_count = len(await get_all("procrastinate_jobs", "id"))
    assert jobs_count == expected_job_count


async def test_finish_job(get_all, pg_job_manager, fetched_job_factory):
    job = await fetched_job_factory(queue="queue_a")

    expected = [{"status": "doing", "attempts": 0}]
    assert await get_all("procrastinate_jobs", "status", "attempts") == expected

    await pg_job_manager.finish_job(
        job=job, status=jobs.Status.SUCCEEDED, delete_job=False
    )

    expected = [{"status": "succeeded", "attempts": 1}]
    assert await get_all("procrastinate_jobs", "status", "attempts") == expected


@pytest.mark.parametrize("delete_job", [False, True])
async def test_finish_job_wrong_initial_status(
    pg_job_manager, fetched_job_factory, delete_job
):
    job = await fetched_job_factory(queue="queue_a")

    # first finish_job to set the job as "failed"
    await pg_job_manager.finish_job(
        job=job, status=jobs.Status.FAILED, delete_job=False
    )

    with pytest.raises(exceptions.ConnectorException) as excinfo:
        await pg_job_manager.finish_job(
            job=job, status=jobs.Status.FAILED, delete_job=delete_job
        )
    assert 'Job was not found or not in "doing" or "todo" status' in str(
        excinfo.value.__cause__
    )


@pytest.mark.parametrize("delete_job", [False, True])
async def test_finish_job_wrong_end_status(
    pg_job_manager, fetched_job_factory, delete_job
):
    job = await fetched_job_factory(queue="queue_a")

    with pytest.raises(exceptions.ConnectorException) as excinfo:
        await pg_job_manager.finish_job(
            job=job, status=jobs.Status.TODO, delete_job=delete_job
        )
    assert 'End status should be either "succeeded", "failed" or "aborted"' in str(
        excinfo.value.__cause__
    )


async def test_retry_job(pg_job_manager, fetched_job_factory):
    job1 = await fetched_job_factory(queue="queue_a")

    await pg_job_manager.retry_job(
        job=job1, retry_at=datetime.datetime.now(datetime.timezone.utc)
    )

    job2 = await pg_job_manager.fetch_job(queues=None)

    assert job2.id == job1.id
    assert job2.attempts == job1.attempts + 1
    assert job2.priority == job1.priority == 0


async def test_retry_job_with_additional_params(pg_job_manager, fetched_job_factory):
    job1 = await fetched_job_factory(queue="queue_a")

    await pg_job_manager.retry_job(
        job=job1,
        retry_at=datetime.datetime.now(datetime.timezone.utc),
        priority=5,
        queue="queue_b",
        lock="some_lock",
    )

    job2 = await pg_job_manager.fetch_job(queues=None)

    assert job2.id == job1.id
    assert job2.attempts == 1
    assert job2.priority == 5
    assert job2.queue == "queue_b"
    assert job2.lock == "some_lock"


async def test_enum_synced(psycopg_connector):
    # If this test breaks, it means you've changed either the task_status PG enum
    # or the python procrastinate.jobs.Status Enum without updating the other.
    pg_enum_rows = await psycopg_connector.execute_query_all_async(
        """SELECT e.enumlabel FROM pg_enum e
               JOIN pg_type t ON e.enumtypid = t.oid WHERE t.typname = %(type_name)s""",
        type_name="procrastinate_job_status",
    )

    pg_values = {row["enumlabel"] for row in pg_enum_rows}
    python_values = {status.value for status in jobs.Status.__members__.values()}
    assert pg_values == python_values


async def test_defer_job(pg_job_manager, get_all, job_factory):
    queue = "marsupilami"
    job = job_factory(
        id=0,
        queue=queue,
        task_name="bob",
        lock="sher",
        queueing_lock="houba",
        task_kwargs={"a": 1, "b": 2},
    )
    new_job = await pg_job_manager.defer_job_async(job=job)

    result = await get_all(
        "procrastinate_jobs",
        "id",
        "args",
        "status",
        "lock",
        "queueing_lock",
        "task_name",
    )
    assert result == [
        {
            "id": new_job.id,
            "args": {"a": 1, "b": 2},
            "status": "todo",
            "lock": "sher",
            "queueing_lock": "houba",
            "task_name": "bob",
        }
    ]


async def test_defer_job_violate_queueing_lock(pg_job_manager, job_factory):
    await pg_job_manager.defer_job_async(
        job_factory(
            id=1,
            queue="queue_a",
            task_name="task_1",
            lock="lock_1",
            queueing_lock="queueing_lock",
            task_kwargs={"a": "b"},
        )
    )
    with pytest.raises(exceptions.AlreadyEnqueued) as excinfo:
        await pg_job_manager.defer_job_async(
            job_factory(
                id=2,
                queue="queue_a",
                task_name="task_2",
                lock="lock_2",
                queueing_lock="queueing_lock",
                task_kwargs={"c": "d"},
            )
        )
    cause = excinfo.value.__cause__
    assert isinstance(cause, exceptions.UniqueViolation)

    # TODO: When QUEUEING_LOCK_CONSTRAINT_LEGACY in manager.py is removed, we can
    # also remove the check for the old constraint name "procrastinate_jobs_queueing_lock_idx"
    assert cause.constraint_name in [
        "procrastinate_jobs_queueing_lock_idx",
        "procrastinate_jobs_queueing_lock_idx_v1",
    ]


async def test_check_connection(pg_job_manager):
    assert await pg_job_manager.check_connection_async() is True


def test_check_connection_sync(pg_job_manager):
    assert pg_job_manager.check_connection() is True


@pytest.fixture
async def fixture_jobs(pg_job_manager, job_factory):
    j1 = job_factory(
        queue="q1",
        lock="lock1",
        queueing_lock="queueing_lock1",
        task_name="task_foo",
        task_kwargs={"key": "a"},
    )
    j1 = await pg_job_manager.defer_job_async(job=j1)

    j2 = job_factory(
        queue="q1",
        lock="lock2",
        queueing_lock="queueing_lock2",
        task_name="task_bar",
        task_kwargs={"key": "b"},
    )
    j2 = await pg_job_manager.defer_job_async(job=j2)
    await pg_job_manager.finish_job(job=j2, status=jobs.Status.FAILED, delete_job=False)

    j3 = job_factory(
        queue="q2",
        lock="lock3",
        queueing_lock="queueing_lock3",
        task_name="task_foo",
        task_kwargs={"key": "c"},
    )
    j3 = await pg_job_manager.defer_job_async(job=j3)
    await pg_job_manager.finish_job(
        job=j3, status=jobs.Status.SUCCEEDED, delete_job=False
    )

    j4 = job_factory(
        queue="q3",
        lock="lock4",
        queueing_lock="queueing_lock4",
        task_name="task_bar",
        task_kwargs={"key": "d"},
    )
    j4 = await pg_job_manager.defer_job_async(job=j4)
    await pg_job_manager.fetch_job(queues=["q3"])

    return [j1, j2, j3, j4]


async def test_list_jobs_dict(fixture_jobs, pg_job_manager):
    j1, *_ = fixture_jobs
    assert (await pg_job_manager.list_jobs_async())[0] == j1


@pytest.mark.parametrize(
    "kwargs, expected",
    [
        ({}, [1, 2, 3, 4]),
        ({"id": 1}, [1]),
        ({"lock": "lock3"}, [3]),
        ({"queue": "q1", "task": "task_foo"}, [1]),
        ({"status": "failed"}, [2]),
        ({"queueing_lock": "queueing_lock2"}, [2]),
    ],
)
async def test_list_jobs(fixture_jobs, kwargs, expected, pg_job_manager):
    assert [
        job.id for job in await pg_job_manager.list_jobs_async(**kwargs)
    ] == expected


async def test_list_queues_dict(fixture_jobs, pg_job_manager):
    assert (await pg_job_manager.list_queues_async())[0] == {
        "name": "q1",
        "jobs_count": 2,
        "todo": 1,
        "doing": 0,
        "succeeded": 0,
        "failed": 1,
        "cancelled": 0,
        "aborted": 0,
    }


@pytest.mark.parametrize(
    "kwargs, expected",
    [
        ({}, ["q1", "q2", "q3"]),
        ({"queue": "q2"}, ["q2"]),
        ({"task": "task_foo"}, ["q1", "q2"]),
        ({"status": "todo"}, ["q1"]),
        ({"lock": "lock2"}, ["q1"]),
    ],
)
async def test_list_queues(fixture_jobs, kwargs, expected, pg_job_manager):
    assert [
        e["name"] for e in await pg_job_manager.list_queues_async(**kwargs)
    ] == expected


async def test_list_tasks_dict(fixture_jobs, pg_job_manager):
    assert (await pg_job_manager.list_tasks_async())[0] == {
        "name": "task_bar",
        "jobs_count": 2,
        "todo": 0,
        "doing": 1,
        "succeeded": 0,
        "failed": 1,
        "cancelled": 0,
        "aborted": 0,
    }


async def test_list_locks_dict(fixture_jobs, pg_job_manager):
    assert {e["name"] for e in await pg_job_manager.list_locks_async()} == {
        "lock1",
        "lock2",
        "lock3",
        "lock4",
    }


@pytest.mark.parametrize(
    "kwargs, expected",
    [
        ({}, ["task_bar", "task_foo"]),
        ({"queue": "q2"}, ["task_foo"]),
        ({"task": "task_foo"}, ["task_foo"]),
        ({"status": "todo"}, ["task_foo"]),
        ({"lock": "lock2"}, ["task_bar"]),
    ],
)
async def test_list_tasks(fixture_jobs, pg_job_manager, kwargs, expected):
    assert [
        e["name"] for e in await pg_job_manager.list_tasks_async(**kwargs)
    ] == expected
