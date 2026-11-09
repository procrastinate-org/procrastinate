from __future__ import annotations

import asyncio
import datetime
import functools

import pytest

from procrastinate import (
    app,
    exceptions,
    job_context,
    jobs,
    manager,
    utils,
    worker,
)
from procrastinate.contrib.aiopg.aiopg_connector import AiopgConnector
from procrastinate.psycopg_connector import PsycopgConnector

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
async def worker_id(pg_job_manager):
    return await pg_job_manager.register_worker()


@pytest.fixture
def fetched_job_factory(deferred_job_factory, pg_job_manager, worker_id):
    async def factory(**kwargs):
        job = await deferred_job_factory(**kwargs)
        fetched_job = await pg_job_manager.fetch_job(queues=None, worker_id=worker_id)
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
    pg_job_manager, deferred_job_factory, job_kwargs, fetch_queues, worker_id
):
    # Now add the job we're testing
    job = await deferred_job_factory(**job_kwargs)

    expected_job = job.evolve(status="doing", worker_id=worker_id)
    assert (
        await pg_job_manager.fetch_job(queues=fetch_queues, worker_id=worker_id)
        == expected_job
    )


async def test_fetch_job_not_fetching_started_job(
    pg_job_manager, fetched_job_factory, worker_id
):
    # Add a first started job
    await fetched_job_factory()

    assert await pg_job_manager.fetch_job(queues=None, worker_id=worker_id) is None


async def test_fetch_job_not_fetching_locked_job(
    pg_job_manager, deferred_job_factory, fetched_job_factory, worker_id
):
    await fetched_job_factory(lock="lock_1")
    await deferred_job_factory(lock="lock_1")

    assert await pg_job_manager.fetch_job(queues=None, worker_id=worker_id) is None


async def test_fetch_job_respect_lock_aborting_job(
    pg_job_manager, deferred_job_factory, fetched_job_factory, worker_id
):
    job = await fetched_job_factory(lock="lock_1")
    await deferred_job_factory(lock="lock_1")

    await pg_job_manager.cancel_job_by_id_async(job.id, abort=True)
    assert await pg_job_manager.fetch_job(queues=None, worker_id=worker_id) is None


async def test_fetch_job_spacial_case_none_lock(
    pg_job_manager, deferred_job_factory, fetched_job_factory, worker_id
):
    await fetched_job_factory(lock=None)
    job = await deferred_job_factory(lock=None)

    assert (
        await pg_job_manager.fetch_job(queues=None, worker_id=worker_id)
    ).id == job.id


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
    pg_job_manager, deferred_job_factory, job_kwargs, fetch_queues, worker_id
):
    await deferred_job_factory(**job_kwargs)

    assert (
        await pg_job_manager.fetch_job(queues=fetch_queues, worker_id=worker_id) is None
    )


@pytest.mark.parametrize(
    "filter_args",
    [
        {"nb_seconds": 1800},
        {"nb_seconds": 1800, "queue": "queue_a"},
        {"nb_seconds": 1800, "task_name": "task_1"},
    ],
)
async def test_get_stalled_jobs_by_started__yes(
    pg_job_manager, fetched_job_factory, psycopg_connector, filter_args
):
    job = await fetched_job_factory(queue="queue_a", task_name="task_1")

    # We fake its started event timestamp
    await psycopg_connector.execute_query_async(
        f"UPDATE procrastinate_events SET at=at - INTERVAL '35 minutes'"
        f"WHERE job_id={job.id}"
    )

    with pytest.warns(DeprecationWarning, match=".*nb_seconds.*"):
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
async def test_get_stalled_jobs_by_started__no(
    pg_job_manager, fetched_job_factory, psycopg_connector, filter_args
):
    job = await fetched_job_factory(queue="queue_a", task_name="task_1")

    # We fake its started event timestamp
    await psycopg_connector.execute_query_async(
        f"UPDATE procrastinate_events SET at=at - INTERVAL '35 minutes'"
        f"WHERE job_id={job.id}"
    )

    with pytest.warns(DeprecationWarning, match=".*nb_seconds.*"):
        result = await pg_job_manager.get_stalled_jobs(**filter_args)
    assert result == []


async def test_get_stalled_jobs_by_started__retries__no(
    pg_job_manager, fetched_job_factory, psycopg_connector
):
    job = await fetched_job_factory(queue="queue_a", task_name="task_1")

    # We fake previous tries
    await psycopg_connector.execute_query_async(
        f"UPDATE procrastinate_events SET at=now() - INTERVAL '1 hour'"
        f"WHERE job_id={job.id} AND type='deferred'"
    )
    await psycopg_connector.execute_query_async(
        f"INSERT INTO procrastinate_events (job_id, type, at) VALUES"
        f"({job.id}, 'started', now() - INTERVAL '1 hour')"
    )
    await psycopg_connector.execute_query_async(
        f"INSERT INTO procrastinate_events (job_id, type, at) VALUES"
        f"({job.id}, 'deferred_for_retry', now() - INTERVAL '59 minutes')"
    )
    events = await psycopg_connector.execute_query_all_async(
        f"SELECT at, type FROM procrastinate_events "
        f"WHERE job_id={job.id} ORDER BY at ASC"
    )

    # Sanity checks: We're in the situation where 1h ago, the job has been deferred,
    # started, it failed so it was retried, and it just started again now.
    assert [e["type"] for e in events] == [
        "deferred",
        "started",
        "deferred_for_retry",
        "started",
    ]

    # It should not be considered stalled
    with pytest.warns(DeprecationWarning, match=".*nb_seconds.*"):
        result = await pg_job_manager.get_stalled_jobs(nb_seconds=1800)
    assert result == []


async def test_get_stalled_jobs_by_started__retries__yes(
    pg_job_manager, fetched_job_factory, psycopg_connector
):
    job = await fetched_job_factory(queue="queue_a", task_name="task_1")

    # We fake previous tries
    await psycopg_connector.execute_query_async(
        f"UPDATE procrastinate_events SET at=now() - INTERVAL '1 hour'"
        f"WHERE job_id={job.id} AND type='deferred'"
    )
    await psycopg_connector.execute_query_async(
        f"UPDATE procrastinate_events SET at=now() - INTERVAL '40 minutes'"
        f"WHERE job_id={job.id} AND type='started'"
    )
    await psycopg_connector.execute_query_async(
        f"INSERT INTO procrastinate_events (job_id, type, at) VALUES"
        f"({job.id}, 'started', now() - INTERVAL '1 hour')"
    )
    await psycopg_connector.execute_query_async(
        f"INSERT INTO procrastinate_events (job_id, type, at) VALUES"
        f"({job.id}, 'deferred_for_retry', now() - INTERVAL '59 minutes')"
    )
    events = await psycopg_connector.execute_query_all_async(
        f"SELECT at, type FROM procrastinate_events "
        f"WHERE job_id={job.id} ORDER BY at ASC"
    )

    # Sanity checks: We're in the situation where 1h ago, the job has been deferred,
    # started, it failed so it was retried, and it started again 40 minutes ago.
    assert [e["type"] for e in events] == [
        "deferred",
        "started",
        "deferred_for_retry",
        "started",
    ]

    # It should not be considered stalled
    with pytest.warns(DeprecationWarning, match=".*nb_seconds.*"):
        result = await pg_job_manager.get_stalled_jobs(nb_seconds=1800)
    assert result == [job]


@pytest.mark.parametrize(
    "filter_args",
    [
        {"queue": "queue_a"},
        {"task_name": "task_1"},
    ],
)
async def test_get_stalled_jobs_by_heartbeat__yes(
    pg_job_manager, fetched_job_factory, psycopg_connector, filter_args
):
    job = await fetched_job_factory(queue="queue_a", task_name="task_1")

    # We fake the worker heartbeat
    await psycopg_connector.execute_query_async(
        "UPDATE procrastinate_workers SET last_heartbeat=last_heartbeat - INTERVAL '35 minutes' "
        f"WHERE id='{job.worker_id}'"
    )

    result = await pg_job_manager.get_stalled_jobs(**filter_args)
    assert result == [job]


@pytest.mark.parametrize(
    "filter_args",
    [
        {"queue": "queue_b"},
        {"task_name": "task_2"},
    ],
)
async def test_get_stalled_jobs_by_heartbeat__no(
    pg_job_manager, fetched_job_factory, psycopg_connector, filter_args
):
    job = await fetched_job_factory(queue="queue_a", task_name="task_1")

    # We fake the worker heartbeat
    await psycopg_connector.execute_query_async(
        "UPDATE procrastinate_workers SET last_heartbeat=last_heartbeat - INTERVAL '35 minutes' "
        f"WHERE id='{job.worker_id}'"
    )

    result = await pg_job_manager.get_stalled_jobs(**filter_args)
    assert result == []


async def test_get_stalled_jobs_by_heartbeat__pruned_worker(
    pg_job_manager, fetched_job_factory, psycopg_connector
):
    job = await fetched_job_factory(queue="queue_a", task_name="task_1")

    # We fake a stalled and pruned worker
    await psycopg_connector.execute_query_async(
        f"DELETE FROM procrastinate_workers WHERE id='{job.worker_id}'"
    )

    result = await pg_job_manager.get_stalled_jobs()
    pruned_job = job.evolve(worker_id=None)
    assert result == [pruned_job]


async def test_register_and_unregister_worker(pg_job_manager, psycopg_connector):
    worker_id = await pg_job_manager.register_worker()
    assert worker_id is not None

    rows = await psycopg_connector.execute_query_all_async(
        f"SELECT * FROM procrastinate_workers WHERE id={worker_id}"
    )
    now = await psycopg_connector.execute_query_one_async(
        "SELECT clock_timestamp() AS now"
    )

    assert len(rows) == 1
    assert rows[0]["id"] == worker_id
    assert abs((rows[0]["last_heartbeat"] - now["now"]).total_seconds()) < 0.1

    await pg_job_manager.unregister_worker(worker_id=worker_id)

    rows = await psycopg_connector.execute_query_all_async(
        f"SELECT * FROM procrastinate_workers WHERE id={worker_id}"
    )
    assert len(rows) == 0


async def test_update_heartbeat(pg_job_manager, psycopg_connector, worker_id):
    rows = await psycopg_connector.execute_query_all_async(
        f"SELECT * FROM procrastinate_workers WHERE id={worker_id}"
    )
    first_heartbeat = rows[0]["last_heartbeat"]

    await pg_job_manager.update_heartbeat(worker_id=worker_id)

    rows = await psycopg_connector.execute_query_all_async(
        f"SELECT * FROM procrastinate_workers WHERE id={worker_id}"
    )
    # The heartbeat is stamped by the database, so the upper bound has to come from
    # the database too: when Postgres runs in a container, its clock can sit a few
    # milliseconds ahead of the host's, which is enough to make a comparison against
    # the local clock fail.
    now = await psycopg_connector.execute_query_one_async(
        "SELECT clock_timestamp() AS now"
    )

    assert len(rows) == 1
    assert rows[0]["id"] == worker_id
    assert first_heartbeat < rows[0]["last_heartbeat"] < now["now"]


async def test_prune_stalled_workers(pg_job_manager, psycopg_connector, worker_id):
    rows = await psycopg_connector.execute_query_all_async(
        f"SELECT * FROM procrastinate_workers WHERE id={worker_id}"
    )
    assert len(rows) == 1

    pruned_workers = await pg_job_manager.prune_stalled_workers(
        seconds_since_heartbeat=1800
    )
    assert pruned_workers == []

    # We fake the heartbeat to be 35 minutes old
    await psycopg_connector.execute_query_async(
        "UPDATE procrastinate_workers "
        "SET last_heartbeat=last_heartbeat - INTERVAL '35 minutes' "
        f"WHERE id='{worker_id}'"
    )

    pruned_workers = await pg_job_manager.prune_stalled_workers(
        seconds_since_heartbeat=1800
    )
    assert pruned_workers == [worker_id]

    rows = await psycopg_connector.execute_query_all_async(
        f"SELECT * FROM procrastinate_workers WHERE id={worker_id}"
    )
    assert len(rows) == 0


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


@pytest.mark.parametrize("replacement", ["waiting", "same_worker", "other_worker"])
@pytest.mark.parametrize(
    "report", ["succeeded", "failed", "aborted", "delete", "retry"]
)
async def test_a_reclaimed_job_ignores_its_previous_worker(
    pg_job_manager, fetched_job_factory, psycopg_connector, replacement, report
):
    """
    Tests that a reclaimed job ignores every report from its previous attempt
    """
    stale_job = await fetched_job_factory(queue="queue_a")
    await psycopg_connector.execute_query_async(
        "UPDATE procrastinate_workers SET last_heartbeat=last_heartbeat - INTERVAL '35 minutes' "
        "WHERE id=%(worker_id)s",
        worker_id=stale_job.worker_id,
    )
    (stalled_job,) = await pg_job_manager.get_stalled_jobs()
    await pg_job_manager.retry_job(
        stalled_job, retry_at=conftest.aware_datetime(2000, 1, 1)
    )
    if replacement != "waiting":
        worker_id = stale_job.worker_id
        if replacement == "other_worker":
            worker_id = await pg_job_manager.register_worker()
        current_job = await pg_job_manager.fetch_job(queues=None, worker_id=worker_id)
        assert current_job.id == stale_job.id
        assert current_job.attempts == stale_job.attempts + 1
    before = await pg_job_manager.list_jobs_async(id=stale_job.id)
    events = await psycopg_connector.execute_query_all_async(
        "SELECT * FROM procrastinate_events WHERE job_id=%(job_id)s ORDER BY id",
        job_id=stale_job.id,
    )
    if report == "retry":
        applied = await pg_job_manager.retry_job(stale_job)
    else:
        status = jobs.Status.SUCCEEDED if report == "delete" else jobs.Status(report)
        applied = await pg_job_manager.finish_job(
            stale_job, status=status, delete_job=report == "delete"
        )
    assert applied is False
    assert await pg_job_manager.list_jobs_async(id=stale_job.id) == before
    assert (
        await psycopg_connector.execute_query_all_async(
            "SELECT * FROM procrastinate_events WHERE job_id=%(job_id)s ORDER BY id",
            job_id=stale_job.id,
        )
        == events
    )
    if replacement == "waiting":
        current_job = await pg_job_manager.fetch_job(
            queues=None, worker_id=stale_job.worker_id
        )
    assert (
        await pg_job_manager.finish_job(
            current_job, status=jobs.Status.SUCCEEDED, delete_job=False
        )
        is True
    )
    assert (
        await pg_job_manager.get_job_status_async(stale_job.id) == jobs.Status.SUCCEEDED
    )


@pytest.mark.parametrize("report", ["finish", "delete", "retry"])
async def test_live_worker_cannot_report_a_reclaimed_attempt(
    psycopg_connector, caplog, report
):
    """
    Tests that a live worker cannot change a job another worker has taken over
    """
    caplog.set_level("DEBUG")
    pg_app = app.App(connector=psycopg_connector)
    started = [asyncio.Event(), asyncio.Event()]
    release = [asyncio.Event(), asyncio.Event()]

    @pg_app.task(pass_context=True)
    async def task_func(context):
        """
        Run one attempt until the test releases it
        """
        attempt = context.job.attempts
        started[attempt].set()
        await release[attempt].wait()
        if attempt == 0 and report == "retry":
            raise exceptions.JobRetry()

    job_id = await task_func.defer_async()
    workers = [
        worker.Worker(
            pg_app,
            name=name,
            wait=False,
            install_signal_handlers=False,
            delete_jobs="always" if report == "delete" else "never",
            update_heartbeat_interval=3600,
            stalled_worker_timeout=3600,
        )
        for name in ("worker_a", "worker_b")
    ]
    runs = [asyncio.create_task(workers[0].run())]
    try:
        await asyncio.wait_for(started[0].wait(), 2)
        await psycopg_connector.execute_query_async(
            "UPDATE procrastinate_workers SET last_heartbeat=last_heartbeat - INTERVAL '35 minutes' "
            "WHERE id=%(worker_id)s",
            worker_id=workers[0].worker_id,
        )
        (stalled_job,) = await pg_app.job_manager.get_stalled_jobs()
        assert await pg_app.job_manager.retry_job(stalled_job) is True
        runs.append(asyncio.create_task(workers[1].run()))
        await asyncio.wait_for(started[1].wait(), 2)
        release[0].set()
        await asyncio.wait_for(runs[0], 2)
        (current_job,) = await pg_app.job_manager.list_jobs_async(id=job_id)
        assert current_job.status == "doing"
        assert current_job.worker_id == workers[1].worker_id
        assert current_job.attempts == 1
        assert any(
            getattr(record, "action", None) == "stale_job_report"
            for record in caplog.records
        )
        assert not any(
            getattr(record, "action", None) == "finish_task"
            and record.job["attempts"] == 0
            for record in caplog.records
        )
        release[1].set()
        await asyncio.wait_for(runs[1], 2)
        rows = await pg_app.job_manager.list_jobs_async(id=job_id)
        if report == "delete":
            assert rows == []
        else:
            assert rows[0].status == "succeeded"
    finally:
        for gate in release:
            gate.set()
        for running_worker in workers:
            running_worker.stop()
        await asyncio.wait_for(asyncio.gather(*runs, return_exceptions=True), 2)


@pytest.mark.parametrize("in_memory", [False, True])
@pytest.mark.parametrize(
    "initial_status, operation, end_status, delete_job, expected_status, expected_attempts, added_events",
    [
        ("todo", "finish", "succeeded", False, "succeeded", 0, ["cancelled"]),
        ("todo", "finish", "failed", False, "failed", 0, ["cancelled"]),
        ("todo", "finish", "aborted", False, "aborted", 0, []),
        ("doing", "finish", "succeeded", False, "succeeded", 1, ["succeeded"]),
        ("doing", "finish", "failed", False, "failed", 1, ["failed"]),
        ("doing", "finish", "aborted", False, "aborted", 1, ["aborted"]),
        ("doing", "finish", "succeeded", True, "deleted", None, []),
        ("failed", "finish", "succeeded", False, "error", None, []),
        ("failed", "finish", "succeeded", True, "error", None, []),
        ("succeeded", "finish", "succeeded", False, "error", None, []),
        ("cancelled", "finish", "succeeded", False, "error", None, []),
        ("aborted", "finish", "succeeded", False, "error", None, []),
        ("doing", "finish", "todo", False, "error", None, []),
        ("doing", "finish", "todo", True, "error", None, []),
        ("todo", "retry", None, False, "error", None, []),
        ("doing", "retry", None, False, "todo", 1, ["scheduled", "deferred_for_retry"]),
        ("failed", "retry", None, False, "todo", 2, ["scheduled", "retried"]),
        ("succeeded", "retry", None, False, "error", None, []),
        ("cancelled", "retry", None, False, "error", None, []),
        ("aborted", "retry", None, False, "error", None, []),
    ],
)
async def test_job_snapshot_mutations_match_postgresql(
    pg_job_manager,
    job_manager,
    job_factory,
    in_memory,
    initial_status,
    operation,
    end_status,
    delete_job,
    expected_status,
    expected_attempts,
    added_events,
):
    """
    Tests that the in-memory connector applies job reports like PostgreSQL
    """
    selected_manager = job_manager if in_memory else pg_job_manager
    deferred_job = await selected_manager.defer_job_async(job_factory(lock=None))
    if initial_status == "cancelled":
        await selected_manager.cancel_job_by_id_async(deferred_job.id)
    elif initial_status != "todo":
        worker_id = await selected_manager.register_worker()
        job = await selected_manager.fetch_job(queues=None, worker_id=worker_id)
        if initial_status != "doing":
            await selected_manager.finish_job_by_id_async(
                job.id, jobs.Status(initial_status), delete_job=False
            )
    (snapshot,) = await selected_manager.list_jobs_async(id=deferred_job.id)
    assert snapshot.status == initial_status
    event_query = (
        "SELECT type FROM procrastinate_events WHERE job_id=%(job_id)s ORDER BY id"
    )
    before_events = (
        list(selected_manager.connector.events.get(snapshot.id, []))
        if in_memory
        else await selected_manager.connector.execute_query_all_async(
            event_query, job_id=snapshot.id
        )
    )
    before_types = [event["type"] for event in before_events]
    if operation == "finish":
        mutation = selected_manager.finish_job(
            snapshot, status=jobs.Status(end_status), delete_job=delete_job
        )
    else:
        mutation = selected_manager.retry_job(
            snapshot, retry_at=conftest.aware_datetime(2000, 1, 1)
        )
    if expected_status == "error":
        with pytest.raises(exceptions.ConnectorException):
            await mutation
    else:
        assert await mutation is True
    rows = await selected_manager.list_jobs_async(id=snapshot.id)
    if expected_status == "deleted":
        assert rows == []
    elif expected_status == "error":
        assert rows == [snapshot]
    else:
        assert rows[0].status == expected_status
        assert rows[0].attempts == expected_attempts
    after_events = (
        selected_manager.connector.events.get(snapshot.id, [])
        if in_memory
        else await selected_manager.connector.execute_query_all_async(
            event_query, job_id=snapshot.id
        )
    )
    expected_events = (
        [] if expected_status == "deleted" else before_types + added_events
    )
    assert [event["type"] for event in after_events] == expected_events


@pytest.mark.parametrize("delete_job", [False, True])
async def test_concurrent_finish_and_retry_apply_only_one_report(
    pg_job_manager, fetched_job_factory, delete_job
):
    """
    Tests that only one of two concurrent reports is applied
    """
    job = await fetched_job_factory(lock=None)
    event_query = (
        "SELECT type FROM procrastinate_events WHERE job_id=%(job_id)s ORDER BY id"
    )
    before_events = await pg_job_manager.connector.execute_query_all_async(
        event_query, job_id=job.id
    )
    results = await asyncio.gather(
        pg_job_manager.finish_job(
            job, status=jobs.Status.SUCCEEDED, delete_job=delete_job
        ),
        pg_job_manager.retry_job(job, retry_at=conftest.aware_datetime(2000, 1, 1)),
    )
    assert sorted(results) == [False, True]
    rows = await pg_job_manager.list_jobs_async(id=job.id)
    if not rows:
        assert delete_job is True
        assert results == [True, False]
        expected_events = []
    else:
        assert rows[0].status == ("succeeded" if results[0] else "todo")
        assert rows[0].attempts == job.attempts + 1
        added_events = (
            ["succeeded"] if results[0] else ["scheduled", "deferred_for_retry"]
        )
        expected_events = [event["type"] for event in before_events] + added_events
    after_events = await pg_job_manager.connector.execute_query_all_async(
        event_query, job_id=job.id
    )
    assert [event["type"] for event in after_events] == expected_events


@pytest.mark.parametrize("report", ["finish", "delete", "retry"])
@pytest.mark.parametrize("changed_field", ["attempts", "status"])
async def test_job_report_rechecks_ownership_after_waiting_for_row_lock(
    psycopg_connector,
    psycopg_connection_params,
    fetched_job_factory,
    report,
    changed_field,
):
    """
    Tests that a report rechecks the job after waiting for its row lock
    """
    job = await fetched_job_factory(lock=None)
    expected_identity = {"status": job.status, "attempts": job.attempts}
    expected_identity[changed_field] = {
        "status": "failed",
        "attempts": job.attempts + 1,
    }[changed_field]
    jobs_query = "SELECT * FROM procrastinate_jobs WHERE id=%(job_id)s"
    events_query = (
        "SELECT * FROM procrastinate_events WHERE job_id=%(job_id)s ORDER BY id"
    )
    report_connector = PsycopgConnector(
        **psycopg_connection_params, min_size=1, max_size=1
    )
    async with app.App(connector=report_connector).open_async() as report_app:
        reporter = await report_connector.execute_query_one_async(
            "SELECT pg_backend_pid() AS pid"
        )
        async with psycopg_connector.pool.connection() as lock_connection:
            report_task = None
            try:
                async with lock_connection.transaction():
                    await lock_connection.execute(
                        "SELECT 1 FROM procrastinate_jobs WHERE id=%s FOR UPDATE",
                        (job.id,),
                    )
                    report_task = asyncio.create_task(
                        report_app.job_manager.retry_job(job)
                        if report == "retry"
                        else report_app.job_manager.finish_job(
                            job, jobs.Status.SUCCEEDED, delete_job=report == "delete"
                        )
                    )
                    loop = asyncio.get_running_loop()
                    deadline = loop.time() + 5
                    while True:
                        waiting = await psycopg_connector.execute_query_one_async(
                            "SELECT wait_event_type = 'Lock' "
                            "AND %(locker_pid)s = ANY(pg_blocking_pids(pid)) AS blocked "
                            "FROM pg_stat_activity WHERE pid=%(reporter_pid)s",
                            locker_pid=lock_connection.info.backend_pid,
                            reporter_pid=reporter["pid"],
                        )
                        if waiting["blocked"]:
                            break
                        assert not report_task.done(), (
                            "Report did not wait for the lock"
                        )
                        assert loop.time() < deadline, "Report did not reach the lock"
                        await asyncio.sleep(0.01)
                    await lock_connection.execute(
                        "UPDATE procrastinate_jobs SET status=%(status)s, "
                        "attempts=%(attempts)s WHERE id=%(job_id)s",
                        {"job_id": job.id, **expected_identity},
                    )
                    before_jobs = (
                        await psycopg_connector.execute_query_all_async_with_connection(
                            lock_connection, jobs_query, job_id=job.id
                        )
                    )
                    before_events = (
                        await psycopg_connector.execute_query_all_async_with_connection(
                            lock_connection, events_query, job_id=job.id
                        )
                    )
                    assert {
                        field: before_jobs[0][field] for field in expected_identity
                    } == expected_identity
                assert await asyncio.wait_for(report_task, 5) is False
                assert (
                    await psycopg_connector.execute_query_all_async(
                        jobs_query, job_id=job.id
                    )
                    == before_jobs
                )
                assert (
                    await psycopg_connector.execute_query_all_async(
                        events_query, job_id=job.id
                    )
                    == before_events
                )
            finally:
                if report_task is not None:
                    report_task.cancel()
                    await asyncio.wait_for(
                        asyncio.gather(report_task, return_exceptions=True), 5
                    )


@pytest.mark.parametrize("in_memory", [False, True])
async def test_retry_abort_requested_attempt(
    pg_job_manager, job_manager, job_factory, in_memory
):
    """
    Tests that retrying an abort-requested attempt fails the job without requeuing it
    """
    selected_manager = job_manager if in_memory else pg_job_manager
    await selected_manager.defer_job_async(job_factory(lock=None))
    worker_id = await selected_manager.register_worker()
    job = await selected_manager.fetch_job(queues=None, worker_id=worker_id)
    await selected_manager.cancel_job_by_id_async(job.id, abort=True)
    retry_at = conftest.aware_datetime(2000, 1, 1)
    assert await selected_manager.retry_job(job, retry_at=retry_at, priority=7) is True
    (failed_job,) = await selected_manager.list_jobs_async(id=job.id)
    assert failed_job.status == "failed"
    assert failed_job.attempts == job.attempts
    assert failed_job.scheduled_at == job.scheduled_at
    assert failed_job.priority == job.priority
    assert failed_job.abort_requested is True
    assert await selected_manager.retry_job(job) is False
    assert (
        await selected_manager.finish_job(
            job, status=jobs.Status.SUCCEEDED, delete_job=False
        )
        is False
    )
    assert await selected_manager.list_jobs_async(id=job.id) == [failed_job]
    with pytest.raises(exceptions.ConnectorException):
        await selected_manager.retry_job(failed_job, retry_at=retry_at)
    assert await selected_manager.list_jobs_async(id=job.id) == [failed_job]


@pytest.mark.parametrize("in_memory", [False, True])
@pytest.mark.parametrize("status", ["failed", "succeeded", "aborted", "cancelled"])
async def test_abort_request_ignores_finished_jobs(
    pg_job_manager, job_manager, job_factory, in_memory, status
):
    """
    Tests that an abort request leaves finished jobs unchanged
    """
    selected_manager = job_manager if in_memory else pg_job_manager
    job = await selected_manager.defer_job_async(job_factory(lock=None))
    if status == "cancelled":
        await selected_manager.cancel_job_by_id_async(job.id)
    else:
        worker_id = await selected_manager.register_worker()
        job = await selected_manager.fetch_job(queues=None, worker_id=worker_id)
        await selected_manager.finish_job(job, jobs.Status(status), delete_job=False)
    (finished_job,) = await selected_manager.list_jobs_async(id=job.id)

    assert await selected_manager.cancel_job_by_id_async(job.id, abort=True) is False
    assert await selected_manager.list_jobs_async(id=job.id) == [finished_job]
    if status == "failed":
        assert await selected_manager.retry_job(finished_job) is True
        assert await selected_manager.get_job_status_async(job.id) == jobs.Status.TODO


@pytest.mark.parametrize("in_memory", [False, True])
async def test_list_job_attempts_to_abort(
    pg_job_manager, job_manager, job_factory, in_memory
):
    """
    Tests listing the attempts of running jobs to abort
    """
    selected_manager = job_manager if in_memory else pg_job_manager
    await selected_manager.defer_job_async(job_factory(queue="queue_a", lock=None))
    worker_id = await selected_manager.register_worker()
    job = await selected_manager.fetch_job(queues=None, worker_id=worker_id)
    assert list(await selected_manager.list_job_attempts_to_abort_async()) == []
    await selected_manager.cancel_job_by_id_async(job.id, abort=True)
    expected = [(job.id, job.attempts)]
    assert list(await selected_manager.list_job_attempts_to_abort_async()) == expected
    assert list(await selected_manager.list_jobs_to_abort_async()) == [job.id]
    assert (
        list(await selected_manager.list_job_attempts_to_abort_async(queue="queue_a"))
        == expected
    )
    assert list(await selected_manager.list_jobs_to_abort_async(queue="queue_b")) == []


@pytest.mark.parametrize("in_memory", [False, True])
async def test_worker_ids_are_not_reused_after_unregister(
    pg_job_manager, job_manager, in_memory
):
    """
    Tests that a new worker never reuses the id of an unregistered one
    """
    selected_manager = job_manager if in_memory else pg_job_manager
    old_worker_id = await selected_manager.register_worker()
    await selected_manager.unregister_worker(old_worker_id)
    new_worker_id = await selected_manager.register_worker()
    assert new_worker_id > old_worker_id
    await selected_manager.unregister_worker(old_worker_id)
    assert await selected_manager.prune_stalled_workers(seconds_since_heartbeat=-1) == [
        new_worker_id
    ]


@pytest.mark.parametrize("in_memory", [False, True])
@pytest.mark.parametrize("abort_source", ["notification", "polling"])
async def test_running_job_receives_abort_after_worker_is_removed(
    psycopg_connector, app, in_memory, abort_source
):
    """
    Tests that a running job can still be aborted after its worker is removed
    """
    selected_app = app if in_memory else app.__class__(connector=psycopg_connector)
    started = asyncio.Event()
    aborted = asyncio.Event()
    release = asyncio.Event()
    contexts = []

    @selected_app.task(pass_context=True)
    async def task_func(context):
        """
        Keep running after the abort until the test releases the job
        """
        contexts.append(context)
        started.set()
        try:
            await release.wait()
        except asyncio.CancelledError:
            aborted.set()
            await release.wait()

    job_id = await task_func.defer_async()
    running_worker = worker.Worker(
        selected_app,
        install_signal_handlers=False,
        listen_notify=False,
        delete_jobs="never",
        update_heartbeat_interval=3600,
        abort_job_polling_interval=0.01 if abort_source == "polling" else 3600,
    )
    run_task = asyncio.create_task(running_worker.run())
    try:
        await asyncio.wait_for(started.wait(), 2)
        await selected_app.job_manager.unregister_worker(running_worker.worker_id)
        (pruned_job,) = await selected_app.job_manager.list_jobs_async(id=job_id)
        assert pruned_job.worker_id is None
        await selected_app.job_manager.cancel_job_by_id_async(job_id, abort=True)
        if abort_source == "notification":
            await running_worker._handle_notification(
                channel="procrastinate_any_queue_v1",
                notification={
                    "type": "abort_job_requested",
                    "job_id": job_id,
                    "attempts": pruned_job.attempts,
                },
            )
        await asyncio.wait_for(aborted.wait(), 2)
        assert contexts[0].should_abort()
        release.set()
        running_worker.stop()
        await asyncio.wait_for(run_task, 2)
        (finished_job,) = await selected_app.job_manager.list_jobs_async(id=job_id)
        assert finished_job.status == "succeeded"
        assert finished_job.worker_id is None
        assert finished_job.attempts == contexts[0].job.attempts + 1
        assert running_worker._job_attempts_to_abort == {}
    finally:
        release.set()
        running_worker.stop()
        await asyncio.wait_for(asyncio.gather(run_task, return_exceptions=True), 2)


@pytest.mark.parametrize(
    "connector_class, pool_args",
    [
        (PsycopgConnector, {"min_size": 1, "max_size": 1}),
        (AiopgConnector, {"minsize": 1, "maxsize": 2}),
    ],
)
@pytest.mark.parametrize("abort_before_start", [False, True])
@pytest.mark.parametrize("remove_worker", [False, True])
async def test_abort_notification_reaches_job_during_fetch_or_execution(
    connector_class,
    pool_args,
    psycopg_connection_params,
    pg_job_manager,
    mocker,
    abort_before_start,
    remove_worker,
):
    """
    Tests that an abort notification reaches a job being fetched or executed
    """
    connection_params = psycopg_connection_params.copy()
    if connector_class is AiopgConnector:
        connection_params["dsn"] = connection_params.pop("conninfo")
    task_connector = connector_class(**connection_params, **pool_args, timeout=0.1)
    started = asyncio.Event()
    fetched = asyncio.Event()
    release_fetch = asyncio.Event()
    listener_started = asyncio.Event()
    notification_handled = asyncio.Event()
    release = asyncio.Event()
    aborted = asyncio.Event()
    executed = False
    loop_notify = task_connector._loop_notify

    async def listen_ready(**kwargs):
        listener_started.set()
        await loop_notify(**kwargs)

    mocker.patch.object(task_connector, "_loop_notify", side_effect=listen_ready)
    async with app.App(connector=task_connector).open_async() as pg_app:

        @pg_app.task(pass_context=True)
        async def task_func(context):
            """
            Hold a pool connection until the job is aborted
            """
            nonlocal executed
            executed = True
            if abort_before_start:
                return
            acquire = (
                task_connector.pool.connection
                if connector_class is PsycopgConnector
                else task_connector.pool.acquire
            )
            async with acquire():
                started.set()
                try:
                    await release.wait()
                except asyncio.CancelledError:
                    assert (
                        context.abort_reason() == job_context.AbortReason.USER_REQUEST
                    )
                    aborted.set()
                    raise

        job_id = await task_func.defer_async()
        running_worker = worker.Worker(
            pg_app,
            concurrency=1,
            wait=False,
            install_signal_handlers=False,
            delete_jobs="never",
            update_heartbeat_interval=3600,
            abort_job_polling_interval=3600,
        )
        fetch_job = pg_app.job_manager.fetch_job
        handle_notification = running_worker._handle_notification

        async def fetch_before_return(**kwargs):
            """
            Pause after fetching so an abort can arrive during the fetch
            """
            job = await fetch_job(**kwargs)
            if job and abort_before_start:
                fetched.set()
                await release_fetch.wait()
            return job

        async def handle_observed(**kwargs):
            """
            Signal the test once an abort notification has been handled
            """
            await handle_notification(**kwargs)
            if kwargs["notification"]["type"] == "abort_job_requested":
                notification_handled.set()

        mocker.patch.object(
            pg_app.job_manager, "fetch_job", side_effect=fetch_before_return
        )
        mocker.patch.object(
            running_worker, "_handle_notification", side_effect=handle_observed
        )
        run_task = asyncio.create_task(running_worker.run())
        try:
            await asyncio.wait_for(
                (fetched if abort_before_start else started).wait(), 2
            )
            await asyncio.wait_for(listener_started.wait(), 2)
            if remove_worker:
                await pg_job_manager.unregister_worker(running_worker.worker_id)
                (pruned_job,) = await pg_job_manager.list_jobs_async(id=job_id)
                assert pruned_job.worker_id is None
            await pg_job_manager.cancel_job_by_id_async(job_id, abort=True)
            await asyncio.wait_for(notification_handled.wait(), 2)
            release_fetch.set()
            if not abort_before_start:
                await asyncio.wait_for(aborted.wait(), 2)
            await asyncio.wait_for(run_task, 2)
            (finished_job,) = await pg_job_manager.list_jobs_async(id=job_id)
            assert finished_job.status == "aborted"
            assert executed is not abort_before_start
        finally:
            release_fetch.set()
            release.set()
            running_worker.stop()
            await asyncio.wait_for(asyncio.gather(run_task, return_exceptions=True), 2)


async def test_delayed_abort_notification_ignores_retried_job(psycopg_connector):
    pg_app = app.App(connector=psycopg_connector)
    started = asyncio.Event()
    release = asyncio.Event()

    @pg_app.task
    async def task_func():
        started.set()
        await release.wait()

    job_id = await task_func.defer_async()
    old_worker_id = await pg_app.job_manager.register_worker()
    old_job = await pg_app.job_manager.fetch_job(queues=None, worker_id=old_worker_id)
    await pg_app.job_manager.cancel_job_by_id_async(job_id, abort=True)
    old_requests = await pg_app.job_manager.list_job_attempts_to_abort_async()
    assert list(old_requests) == [(job_id, 0)]
    assert (
        await pg_app.job_manager.finish_job(
            old_job, status=jobs.Status.FAILED, delete_job=False
        )
        is True
    )
    (failed_job,) = await pg_app.job_manager.list_jobs_async(id=job_id)
    assert await pg_app.job_manager.retry_job(failed_job) is True
    running_worker = worker.Worker(
        pg_app,
        wait=False,
        install_signal_handlers=False,
        delete_jobs="never",
        abort_job_polling_interval=3600,
        listen_notify=False,
    )
    run_task = asyncio.create_task(running_worker.run())
    try:
        await asyncio.wait_for(started.wait(), 2)
        notification = {
            "type": "abort_job_requested",
            "job_id": job_id,
            "attempts": old_job.attempts,
        }
        await running_worker._handle_notification(
            channel="procrastinate_any_queue_v1",
            notification=notification,
        )
        running_worker._handle_abort_jobs_requested(old_requests)
        (context,) = running_worker._running_jobs.values()
        assert not context.should_abort()
        assert (
            await pg_app.job_manager.get_job_status_async(job_id) == jobs.Status.DOING
        )
        await pg_app.job_manager.cancel_job_by_id_async(job_id, abort=True)
        notification["attempts"] = context.job.attempts
        await running_worker._handle_notification(
            channel="procrastinate_any_queue_v1",
            notification=notification,
        )
        await asyncio.wait_for(run_task, 2)
        assert (
            await pg_app.job_manager.get_job_status_async(job_id) == jobs.Status.ABORTED
        )
    finally:
        release.set()
        running_worker.stop()
        await asyncio.wait_for(asyncio.gather(run_task, return_exceptions=True), 2)


async def test_aborted_retry_ignores_its_previous_delivery(
    pg_job_manager, fetched_job_factory
):
    stale_job = await fetched_job_factory()
    await pg_job_manager.cancel_job_by_id_async(stale_job.id, abort=True)
    await pg_job_manager.retry_job_by_id_async(
        stale_job.id, retry_at=conftest.aware_datetime(2000, 1, 1)
    )
    (failed_job,) = await pg_job_manager.list_jobs_async(id=stale_job.id)
    assert failed_job.status == "failed"
    assert failed_job.attempts == stale_job.attempts
    assert await pg_job_manager.retry_job(stale_job) is False
    assert await pg_job_manager.list_jobs_async(id=stale_job.id) == [failed_job]


async def test_retry_pruned_stalled_worker(pg_job_manager, fetched_job_factory):
    stale_job = await fetched_job_factory()
    await pg_job_manager.unregister_worker(stale_job.worker_id)
    (pruned_job,) = await pg_job_manager.get_stalled_jobs()
    assert pruned_job.worker_id is None
    assert (
        await pg_job_manager.retry_job(
            pruned_job, retry_at=conftest.aware_datetime(2000, 1, 1)
        )
        is True
    )
    assert await pg_job_manager.retry_job(stale_job) is False
    worker_id = await pg_job_manager.register_worker()
    current_job = await pg_job_manager.fetch_job(queues=None, worker_id=worker_id)
    assert current_job.id == stale_job.id
    assert current_job.attempts == stale_job.attempts + 1
    assert (
        await pg_job_manager.finish_job(
            stale_job, status=jobs.Status.SUCCEEDED, delete_job=False
        )
        is False
    )
    assert (
        await pg_job_manager.finish_job(
            current_job, status=jobs.Status.SUCCEEDED, delete_job=False
        )
        is True
    )


@pytest.mark.parametrize("in_memory", [False, True])
@pytest.mark.parametrize(
    "report, expected",
    [
        ("finish", [("succeeded", 1)]),
        ("delete", []),
        ("retry", [("todo", 1)]),
    ],
)
async def test_pruned_worker_can_report_its_unclaimed_attempt(
    pg_job_manager, job_manager, job_factory, in_memory, report, expected
):
    """
    Tests that a pruned worker can report an attempt nobody else has claimed
    """
    selected_manager = job_manager if in_memory else pg_job_manager
    await selected_manager.defer_job_async(job_factory(lock=None))
    worker_id = await selected_manager.register_worker()
    job = await selected_manager.fetch_job(queues=None, worker_id=worker_id)
    await selected_manager.unregister_worker(worker_id)
    if report == "retry":
        applied = await selected_manager.retry_job(job)
    else:
        applied = await selected_manager.finish_job(
            job, jobs.Status.SUCCEEDED, delete_job=report == "delete"
        )
    assert applied is True
    rows = await selected_manager.list_jobs_async(id=job.id)
    assert [(row.status, row.attempts) for row in rows] == expected


async def test_retry_current_failed_snapshot(pg_job_manager, fetched_job_factory):
    job = await fetched_job_factory()
    assert (
        await pg_job_manager.finish_job(
            job, status=jobs.Status.FAILED, delete_job=False
        )
        is True
    )
    (failed_job,) = await pg_job_manager.list_jobs_async(id=job.id)
    assert await pg_job_manager.retry_job(failed_job) is True
    assert await pg_job_manager.retry_job(failed_job) is False
    assert await pg_job_manager.get_job_status_async(job.id) == jobs.Status.TODO


@pytest.mark.parametrize("delete_job", [False, True])
async def test_finish_job_by_id_keeps_administrative_behavior(
    pg_job_manager, deferred_job_factory, job_factory, get_all, delete_job
):
    """
    Tests that finishing requires a captured job unless it goes through the by-id method
    """
    job = await deferred_job_factory()
    events = await get_all("procrastinate_events", "*")
    with pytest.raises(ValueError, match="finish_job_by_id_async"):
        await pg_job_manager.finish_job(
            job_factory(id=job.id), jobs.Status.SUCCEEDED, delete_job=delete_job
        )
    assert await pg_job_manager.list_jobs_async(id=job.id) == [job]
    assert await get_all("procrastinate_events", "*") == events

    await pg_job_manager.finish_job_by_id_async(
        job.id, jobs.Status.SUCCEEDED, delete_job=delete_job
    )
    rows = await pg_job_manager.list_jobs_async(id=job.id)
    if delete_job:
        assert rows == []
    else:
        assert rows[0].status == "succeeded"
        assert rows[0].attempts == 0


@pytest.mark.parametrize("status", ["doing", "failed"])
async def test_retry_job_by_id_keeps_administrative_behavior(
    pg_job_manager, fetched_job_factory, job_factory, get_all, status
):
    """
    Tests that retrying requires a captured job unless it goes through the by-id method
    """
    job = await fetched_job_factory()
    if status == "failed":
        await pg_job_manager.finish_job_by_id_async(
            job.id, jobs.Status.FAILED, delete_job=False
        )
    (current_job,) = await pg_job_manager.list_jobs_async(id=job.id)
    events = await get_all("procrastinate_events", "*")
    with pytest.raises(ValueError, match="retry_job_by_id_async"):
        await pg_job_manager.retry_job(job_factory(id=job.id))
    assert await pg_job_manager.list_jobs_async(id=job.id) == [current_job]
    assert await get_all("procrastinate_events", "*") == events

    await pg_job_manager.retry_job_by_id_async(
        job.id, retry_at=conftest.aware_datetime(2000, 1, 1)
    )
    (retried_job,) = await pg_job_manager.list_jobs_async(id=job.id)
    assert retried_job.status == "todo"
    assert retried_job.attempts == current_job.attempts + 1


@pytest.mark.parametrize("delete_job", [False, True])
async def test_finish_job_ignores_finished_attempt(
    pg_job_manager, fetched_job_factory, delete_job
):
    job = await fetched_job_factory(queue="queue_a")

    await pg_job_manager.finish_job(
        job=job, status=jobs.Status.FAILED, delete_job=False
    )

    assert (
        await pg_job_manager.finish_job(
            job=job, status=jobs.Status.FAILED, delete_job=delete_job
        )
        is False
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


async def test_retry_job(pg_job_manager, fetched_job_factory, worker_id):
    job1 = await fetched_job_factory(queue="queue_a")

    await pg_job_manager.retry_job(
        job=job1, retry_at=datetime.datetime.now(datetime.timezone.utc)
    )

    job2 = await pg_job_manager.fetch_job(queues=None, worker_id=worker_id)

    assert job2.id == job1.id
    assert job2.attempts == job1.attempts + 1
    assert job2.priority == job1.priority == 0


async def test_retry_job_with_additional_params(
    pg_job_manager, fetched_job_factory, worker_id
):
    job1 = await fetched_job_factory(queue="queue_a")

    await pg_job_manager.retry_job(
        job=job1,
        retry_at=datetime.datetime.now(datetime.timezone.utc),
        priority=5,
        queue="queue_b",
        lock="some_lock",
    )

    job2 = await pg_job_manager.fetch_job(queues=None, worker_id=worker_id)

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


@pytest.mark.parametrize("is_async", [False, True])
async def test_defer_captured_job_resets_attempt_identity(
    pg_job_manager, fetched_job_factory, is_async
):
    """
    Tests that deferring a captured job returns it with reset attempt metadata
    """
    original = await fetched_job_factory(lock=None, queueing_lock=None)
    await pg_job_manager.retry_job(original)
    original = await pg_job_manager.fetch_job(queues=None, worker_id=original.worker_id)
    await pg_job_manager.cancel_job_by_id_async(original.id, abort=True)
    (original,) = await pg_job_manager.list_jobs_async(id=original.id)
    assert original.attempts == 1
    assert original.abort_requested

    if is_async:
        new_job = await pg_job_manager.defer_job_async(original)
    else:
        new_job = await utils.sync_to_async(pg_job_manager.defer_job, original)

    assert new_job.id != original.id
    assert (
        await pg_job_manager.finish_job(
            new_job, status=jobs.Status.SUCCEEDED, delete_job=False
        )
        is True
    )
    assert new_job.worker_id is None
    assert new_job.attempts == 0
    assert not new_job.abort_requested
    assert await pg_job_manager.list_jobs_async(id=original.id) == [original]


async def test_batch_defer_jobs(pg_job_manager, get_all, job_factory):
    queue = "marsupilami"
    new_jobs = await pg_job_manager.batch_defer_jobs_async(
        jobs=[
            job_factory(
                id=0,
                queue=queue,
                task_name="bob",
                lock="sher",
                queueing_lock="houba1",
                task_kwargs={"a": 1, "b": 2},
            ),
            job_factory(
                id=0,
                queue=queue,
                task_name="bob",
                lock="sher",
                queueing_lock="houba2",
                task_kwargs={"a": 3, "b": 4},
            ),
        ]
    )

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
            "id": new_jobs[0].id,
            "args": {"a": 1, "b": 2},
            "status": "todo",
            "lock": "sher",
            "queueing_lock": "houba1",
            "task_name": "bob",
        },
        {
            "id": new_jobs[1].id,
            "args": {"a": 3, "b": 4},
            "status": "todo",
            "lock": "sher",
            "queueing_lock": "houba2",
            "task_name": "bob",
        },
    ]


async def test_defer_job_violate_queueing_lock(pg_job_manager, job_factory):
    await pg_job_manager.defer_job_async(
        job_factory(
            id=1,
            queue="queue_a",
            task_name="task_1",
            lock="lock_1",
            queueing_lock="same_queueing_lock",
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
                queueing_lock="same_queueing_lock",
                task_kwargs={"c": "d"},
            )
        )
    cause = excinfo.value.__cause__
    assert isinstance(cause, exceptions.UniqueViolation)

    assert cause.constraint_name == "procrastinate_jobs_queueing_lock_idx_v1"

    assert cause.queueing_lock == "same_queueing_lock"


async def test_batch_defer_jobs_violate_queueing_lock(
    pg_job_manager, get_all, job_factory
):
    with pytest.raises(exceptions.AlreadyEnqueued) as excinfo:
        await pg_job_manager.batch_defer_jobs_async(
            [
                job_factory(
                    id=1,
                    queue="queue_a",
                    task_name="task_1",
                    lock="lock_1",
                    queueing_lock="same_queueing_lock",
                    task_kwargs={"a": "b"},
                ),
                job_factory(
                    id=2,
                    queue="queue_a",
                    task_name="task_2",
                    lock="lock_2",
                    queueing_lock="same_queueing_lock",
                    task_kwargs={"c": "d"},
                ),
            ]
        )
    cause = excinfo.value.__cause__
    assert isinstance(cause, exceptions.UniqueViolation)
    assert cause.queueing_lock == "same_queueing_lock"

    assert cause.constraint_name == "procrastinate_jobs_queueing_lock_idx_v1"

    assert await get_all("procrastinate_jobs", "id") == []


async def test_check_connection(pg_job_manager):
    assert await pg_job_manager.check_connection_async() is True


def test_check_connection_sync(pg_job_manager):
    assert pg_job_manager.check_connection() is True


@pytest.fixture
async def fixture_jobs(pg_job_manager, job_factory, worker_id):
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
    await pg_job_manager.fetch_job(queues=["q3"], worker_id=worker_id)

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
