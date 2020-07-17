import datetime

import psycopg2.errors
import pytest

from procrastinate import exceptions, jobs, store

from .. import conftest

pytestmark = pytest.mark.asyncio


@pytest.fixture
def pg_job_store(aiopg_connector):
    return store.JobStore(connector=aiopg_connector)


@pytest.fixture
def get_all(aiopg_connector):
    async def f(table, *fields):
        return await aiopg_connector.execute_query_all_async(
            f"SELECT {', '.join(fields)} FROM {table}"
        )

    return f


@pytest.mark.parametrize(
    "job_kwargs",
    [
        {"queue": "queue_a"},
        {"queue": "queue_a", "scheduled_at": conftest.aware_datetime(2000, 1, 1)},
    ],
)
async def test_fetch_job(pg_job_store, job_factory, job_kwargs):
    # Add a first started job
    job = job_factory(id=2, **job_kwargs)
    await pg_job_store.defer_job_async(job_factory(queue="queue_a"))
    await pg_job_store.fetch_job(queues=None)

    # Now add the job we're testing
    await pg_job_store.defer_job_async(job)

    assert await pg_job_store.fetch_job(queues=["queue_a"]) == job


@pytest.mark.parametrize(
    "job_kwargs",
    [
        # We won't see this one because of the lock
        {"queue": "queue_a", "lock": "lock_1"},
        # We won't see this one because of the queue
        {"queue": "queue_b"},
        # We won't see this one because of the scheduled date
        {"queue": "queue_a", "scheduled_at": conftest.aware_datetime(2100, 1, 1)},
    ],
)
async def test_get_job_no_result(pg_job_store, job_factory, job_kwargs):
    job = job_factory(**job_kwargs)

    # Add a first started job
    await pg_job_store.defer_job_async(job_factory(lock="lock_1"))
    await pg_job_store.fetch_job(queues=None)

    # Now add the job we're testing
    await pg_job_store.defer_job_async(job)

    assert await pg_job_store.fetch_job(queues=["queue_a"]) is None


async def test_get_stalled_jobs(get_all, pg_job_store, aiopg_connector, job_factory):
    await pg_job_store.defer_job_async(job_factory(queue="queue_a", task_name="task_1"))
    job_id = (await get_all("procrastinate_jobs", "id"))[0]["id"]

    # No started job
    assert await pg_job_store.get_stalled_jobs(nb_seconds=3600) == []

    # We start a job and fake its `started` state in the database
    job = await pg_job_store.fetch_job(queues=["queue_a"])
    await aiopg_connector.execute_query_async(
        "INSERT INTO procrastinate_events(job_id, type, at) VALUES "
        "(%(job_id)s, 'started', NOW() - INTERVAL '30 minutes')",
        job_id=job_id,
    )

    # Nb_seconds parameter
    assert await pg_job_store.get_stalled_jobs(nb_seconds=3600) == []
    assert await pg_job_store.get_stalled_jobs(nb_seconds=1800) == [job]

    # Queue parameter
    assert await pg_job_store.get_stalled_jobs(nb_seconds=1800, queue="queue_a") == [
        job
    ]
    assert await pg_job_store.get_stalled_jobs(nb_seconds=1800, queue="queue_b") == []
    # Task name parameter
    assert await pg_job_store.get_stalled_jobs(nb_seconds=1800, task_name="task_1") == [
        job
    ]
    assert (
        await pg_job_store.get_stalled_jobs(nb_seconds=1800, task_name="task_2") == []
    )


async def test_delete_old_jobs_job_is_not_finished(
    get_all, pg_job_store, aiopg_connector, job_factory
):
    await pg_job_store.defer_job_async(job_factory(queue="queue_a"))

    # No started job
    await pg_job_store.delete_old_jobs(nb_hours=0)
    assert len(await get_all("procrastinate_jobs", "id")) == 1

    # We start a job
    job = await pg_job_store.fetch_job(queues=["queue_a"])
    # We back date the started event
    await aiopg_connector.execute_query_async(
        f"UPDATE procrastinate_events SET at=at - INTERVAL '2 hours'"
        f"WHERE job_id={job.id}"
    )

    # The job is not finished so it's not deleted
    await pg_job_store.delete_old_jobs(nb_hours=0)
    assert len(await get_all("procrastinate_jobs", "id")) == 1


async def test_delete_old_jobs_multiple_jobs(
    get_all, pg_job_store, aiopg_connector, job_factory
):
    await pg_job_store.defer_job_async(job_factory(queue="queue_a"))
    await pg_job_store.defer_job_async(job_factory(queue="queue_b"))

    # We start both jobs
    job_a = await pg_job_store.fetch_job(queues=["queue_a"])
    job_b = await pg_job_store.fetch_job(queues=["queue_b"])
    # We finish both jobs
    await pg_job_store.finish_job(job_a, status=jobs.Status.SUCCEEDED)
    await pg_job_store.finish_job(job_b, status=jobs.Status.SUCCEEDED)
    # We back date the events for job_a
    await aiopg_connector.execute_query_async(
        f"UPDATE procrastinate_events SET at=at - INTERVAL '2 hours'"
        f"WHERE job_id={job_a.id}"
    )

    # Only job_a is deleted
    await pg_job_store.delete_old_jobs(nb_hours=2)
    rows = await get_all("procrastinate_jobs", "id")
    assert len(rows) == 1
    assert rows[0]["id"] == job_b.id


async def test_delete_old_job_filter_on_end_date(
    get_all, pg_job_store, aiopg_connector, job_factory
):
    await pg_job_store.defer_job_async(job_factory(queue="queue_a"))
    # We start the job
    job = await pg_job_store.fetch_job(queues=["queue_a"])
    # We finish the job
    await pg_job_store.finish_job(job, status=jobs.Status.SUCCEEDED)
    # We back date only the start event
    await aiopg_connector.execute_query_async(
        f"UPDATE procrastinate_events SET at=at - INTERVAL '2 hours'"
        f"WHERE job_id={job.id} AND TYPE='started'"
    )

    # Job is not deleted since it finished recently
    await pg_job_store.delete_old_jobs(nb_hours=2)
    rows = await get_all("procrastinate_jobs", "id")
    assert len(rows) == 1


@pytest.mark.parametrize(
    "status, nb_hours, queue, include_error, should_delete",
    [
        # nb_hours
        (jobs.Status.SUCCEEDED, 1, None, False, True),
        (jobs.Status.SUCCEEDED, 3, None, False, False),
        # queue
        (jobs.Status.SUCCEEDED, 1, "queue_a", False, True),
        (jobs.Status.SUCCEEDED, 3, "queue_a", False, False),
        (jobs.Status.SUCCEEDED, 1, "queue_b", False, False),
        (jobs.Status.SUCCEEDED, 1, "queue_b", False, False),
        # include_error
        (jobs.Status.FAILED, 1, None, False, False),
        (jobs.Status.FAILED, 1, None, True, True),
    ],
)
async def test_delete_old_jobs_parameters(
    get_all,
    pg_job_store,
    aiopg_connector,
    status,
    nb_hours,
    queue,
    include_error,
    should_delete,
    job_factory,
):
    await pg_job_store.defer_job_async(job_factory(queue="queue_a"))

    # We start a job
    job = await pg_job_store.fetch_job(queues=["queue_a"])
    # We finish the job
    await pg_job_store.finish_job(job, status=status)
    # We back date its events
    await aiopg_connector.execute_query_async(
        f"UPDATE procrastinate_events SET at=at - INTERVAL '2 hours'"
        f"WHERE job_id={job.id}"
    )

    await pg_job_store.delete_old_jobs(
        nb_hours=nb_hours, queue=queue, include_error=include_error
    )
    nb_jobs = len(await get_all("procrastinate_jobs", "id"))
    if should_delete:
        assert nb_jobs == 0
    else:
        assert nb_jobs == 1


async def test_finish_job(get_all, pg_job_store, job_factory):
    await pg_job_store.defer_job_async(job_factory(queue="queue_a"))
    job = await pg_job_store.fetch_job(queues=["queue_a"])

    assert await get_all("procrastinate_jobs", "status") == [{"status": "doing"}]
    events = await get_all("procrastinate_events", "type", "at")
    events_started = list(filter(lambda e: e["type"] == "started", events))
    assert len(events_started) == 1
    started_at = events_started[0]["at"]
    assert started_at.date() == datetime.datetime.utcnow().date()
    assert await get_all("procrastinate_jobs", "attempts") == [{"attempts": 0}]

    await pg_job_store.finish_job(job=job, status=jobs.Status.SUCCEEDED)
    expected = [{"status": "succeeded", "attempts": 1}]
    assert await get_all("procrastinate_jobs", "status", "attempts") == expected


async def test_finish_job_retry(get_all, pg_job_store, job_factory):
    await pg_job_store.defer_job_async(job_factory())
    job1 = await pg_job_store.fetch_job(queues=None)
    await pg_job_store.finish_job(job=job1, status=jobs.Status.TODO)

    job2 = await pg_job_store.fetch_job(queues=None)

    assert job2.id == job1.id
    assert job2.attempts == job1.attempts + 1


async def test_enum_synced(aiopg_connector):
    # If this test breaks, it means you've changed either the task_status PG enum
    # or the python procrastinate.jobs.Status Enum without updating the other.
    pg_enum_rows = await aiopg_connector.execute_query_all_async(
        """SELECT e.enumlabel FROM pg_enum e
               JOIN pg_type t ON e.enumtypid = t.oid WHERE t.typname = %(type_name)s""",
        type_name="procrastinate_job_status",
    )

    pg_values = {row["enumlabel"] for row in pg_enum_rows}
    python_values = {status.value for status in jobs.Status.__members__.values()}
    assert pg_values == python_values


async def test_defer_job(pg_job_store, get_all, job_factory):
    queue = "marsupilami"
    job = job_factory(
        id=0,
        queue=queue,
        task_name="bob",
        lock="sher",
        queueing_lock="houba",
        task_kwargs={"a": 1, "b": 2},
    )
    pk = await pg_job_store.defer_job_async(job=job)

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
            "id": pk,
            "args": {"a": 1, "b": 2},
            "status": "todo",
            "lock": "sher",
            "queueing_lock": "houba",
            "task_name": "bob",
        }
    ]


async def test_defer_job_violate_queueing_lock(pg_job_store, job_factory):
    await pg_job_store.defer_job_async(
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
        await pg_job_store.defer_job_async(
            job_factory(
                id=2,
                queue="queue_a",
                task_name="task_2",
                lock="lock_2",
                queueing_lock="queueing_lock",
                task_kwargs={"c": "d"},
            )
        )
        assert isinstance(excinfo.value.__cause__, psycopg2.errors.UniqueViolation)
        assert (
            excinfo.value.__cause__.diag.constraint_name
            == "procrastinate_jobs_queueing_lock_idx"
        )
