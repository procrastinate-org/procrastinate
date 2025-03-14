from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock

import pytest

from procrastinate import exceptions, utils

from .. import conftest


def test_reset(connector):
    connector.jobs = {1: {}}
    connector.reset()
    assert connector.jobs == {}


async def test_generic_execute(connector):
    result = {}
    connector.reverse_queries = {"a": "b"}

    async def b(**kwargs):
        result.update(kwargs)

    connector.b_youpi = b

    await connector.generic_execute("a", "youpi", i="j")

    assert result == {"i": "j"}


async def test_execute_query(connector):
    connector.generic_execute = AsyncMock()
    await connector.execute_query_async("a", b="c")
    connector.generic_execute.assert_called_with("a", "run", b="c")


async def test_execute_query_one(connector):
    connector.generic_execute = AsyncMock()
    assert (
        await connector.execute_query_one_async("a", b="c")
        == connector.generic_execute.return_value
    )
    connector.generic_execute.assert_called_with("a", "one", b="c")


async def test_execute_query_all_async(connector):
    connector.generic_execute = AsyncMock()
    assert (
        await connector.execute_query_all_async("a", b="c")
        == connector.generic_execute.return_value
    )
    connector.generic_execute.assert_called_with("a", "all", b="c")


def test_make_dynamic_query(connector):
    assert connector.make_dynamic_query("foo {bar}", bar="baz") == "foo baz"


async def test_defer_job_one(connector):
    job = await connector.defer_job_one(
        task_name="mytask",
        priority=5,
        lock="sher",
        queueing_lock="houba",
        args={"a": "b"},
        scheduled_at=None,
        queue="marsupilami",
    )

    assert connector.jobs == {
        1: {
            "id": 1,
            "queue_name": "marsupilami",
            "priority": 5,
            "task_name": "mytask",
            "lock": "sher",
            "queueing_lock": "houba",
            "args": {"a": "b"},
            "status": "todo",
            "scheduled_at": None,
            "attempts": 0,
            "abort_requested": False,
            "worker_id": None,
        }
    }
    assert connector.jobs[1] == job


async def test_defer_job_one_multiple_times(connector):
    await connector.defer_job_one(
        task_name="mytask",
        priority=0,
        lock=None,
        queueing_lock=None,
        args={},
        scheduled_at=None,
        queue="default",
    )
    await connector.defer_job_one(
        task_name="mytask",
        priority=0,
        lock=None,
        queueing_lock=None,
        args={},
        scheduled_at=None,
        queue="default",
    )
    assert len(connector.jobs) == 2


async def test_defer_same_job_with_queueing_lock_second_time_after_first_one_succeeded(
    connector,
):
    job_data = {
        "task_name": "mytask",
        "priority": 0,
        "lock": None,
        "queueing_lock": "some-lock",
        "args": {},
        "scheduled_at": None,
        "queue": "default",
    }

    # 1. Defer job with queueing-lock
    job_row = await connector.defer_job_one(**job_data)
    assert len(connector.jobs) == 1

    # 2. Defering a second time should fail, as first one
    #    still in state `todo`
    with pytest.raises(exceptions.UniqueViolation):
        await connector.defer_job_one(**job_data)
    assert len(connector.jobs) == 1

    # 3. Finish first job
    await connector.finish_job_run(
        job_id=job_row["id"], status="finished", delete_job=False
    )

    # 4. Defering a second time should work now,
    #    as first job in state `finished`
    await connector.defer_job_one(**job_data)
    assert len(connector.jobs) == 2


def test_current_locks(connector):
    connector.jobs = {
        1: {"status": "todo", "lock": "foo"},
        2: {"status": "doing", "lock": "yay"},
    }
    assert connector.current_locks == {"yay"}


def test_finished_jobs(connector):
    connector.jobs = {
        1: {"status": "todo"},
        2: {"status": "doing"},
        3: {"status": "succeeded"},
        4: {"status": "failed"},
    }
    assert connector.finished_jobs == [{"status": "succeeded"}, {"status": "failed"}]


async def test_select_stalled_jobs_all(connector):
    connector.jobs = {
        # We're not selecting this job because it's "succeeded"
        1: {
            "id": 1,
            "status": "succeeded",
            "queue_name": "marsupilami",
            "task_name": "mytask",
        },
        # This one because it's the wrong queue
        2: {
            "id": 2,
            "status": "doing",
            "queue_name": "other_queue",
            "task_name": "mytask",
        },
        # This one because of the task
        3: {
            "id": 3,
            "status": "doing",
            "queue_name": "marsupilami",
            "task_name": "my_other_task",
        },
        # This one because it's not stalled
        4: {
            "id": 4,
            "status": "doing",
            "queue_name": "marsupilami",
            "task_name": "mytask",
        },
        # We're taking this one.
        5: {
            "id": 5,
            "status": "doing",
            "queue_name": "marsupilami",
            "task_name": "mytask",
        },
        # And this one
        6: {
            "id": 6,
            "status": "doing",
            "queue_name": "marsupilami",
            "task_name": "mytask",
        },
    }
    connector.events = {
        1: [{"at": conftest.aware_datetime(2000, 1, 1)}],
        2: [{"at": conftest.aware_datetime(2000, 1, 1)}],
        3: [{"at": conftest.aware_datetime(2000, 1, 1)}],
        4: [{"at": conftest.aware_datetime(2100, 1, 1)}],
        5: [{"at": conftest.aware_datetime(2000, 1, 1)}],
        6: [{"at": conftest.aware_datetime(2000, 1, 1)}],
    }

    results = await connector.select_stalled_jobs_all(
        queue="marsupilami", task_name="mytask", nb_seconds=0
    )
    assert [job["id"] for job in results] == [5, 6]


async def test_select_stalled_workers_all(connector):
    worker_id1 = utils.create_worker_id()
    worker_id2 = utils.create_worker_id()
    worker_id3 = utils.create_worker_id()

    connector.heartbeats = {
        worker_id1: conftest.aware_datetime(2000, 1, 1),
        worker_id2: conftest.aware_datetime(2000, 1, 1),
        worker_id3: conftest.aware_datetime(2100, 1, 1),
    }

    results = await connector.select_stalled_workers_all(seconds_since_heartbeat=0)
    assert results == [
        {"worker_id": worker_id1},
        {"worker_id": worker_id2},
    ]


async def test_delete_old_jobs_run(connector):
    connector.jobs = {
        # We're not deleting this job because it's "doing"
        1: {"id": 1, "status": "doing", "queue_name": "marsupilami"},
        # This one because it's the wrong queue
        2: {"id": 2, "status": "succeeded", "queue_name": "other_queue"},
        # This one is not old enough
        3: {"id": 3, "status": "succeeded", "queue_name": "marsupilami"},
        # This one we delete
        4: {"id": 4, "status": "succeeded", "queue_name": "marsupilami"},
    }
    connector.events = {
        1: [{"type": "succeeded", "at": conftest.aware_datetime(2000, 1, 1)}],
        2: [{"type": "succeeded", "at": conftest.aware_datetime(2000, 1, 1)}],
        3: [{"type": "succeeded", "at": utils.utcnow()}],
        4: [{"type": "succeeded", "at": conftest.aware_datetime(2000, 1, 1)}],
    }

    await connector.delete_old_jobs_run(
        queue="marsupilami", statuses=("succeeded"), nb_hours=0
    )
    assert 4 not in connector.jobs


async def test_fetch_job_one(connector, worker_id):
    # This one will be selected, then skipped the second time because it's processing
    await connector.defer_job_one(
        task_name="mytask",
        priority=0,
        args={},
        queue="marsupilami",
        scheduled_at=None,
        lock="a",
        queueing_lock="a",
    )

    # This one because it's the wrong queue
    await connector.defer_job_one(
        task_name="mytask",
        priority=0,
        args={},
        queue="other_queue",
        scheduled_at=None,
        lock="b",
        queueing_lock="b",
    )
    # This one because of the scheduled_at
    await connector.defer_job_one(
        task_name="mytask",
        priority=0,
        args={},
        queue="marsupilami",
        scheduled_at=conftest.aware_datetime(2100, 1, 1),
        lock="c",
        queueing_lock="c",
    )
    # This one because of the lock
    await connector.defer_job_one(
        task_name="mytask",
        priority=0,
        args={},
        queue="marsupilami",
        scheduled_at=None,
        lock="a",
        queueing_lock="d",
    )
    # We're taking this one.
    await connector.defer_job_one(
        task_name="mytask",
        priority=0,
        args={},
        queue="marsupilami",
        scheduled_at=None,
        lock="e",
        queueing_lock="e",
    )

    assert (await connector.fetch_job_one(queues=["marsupilami"], worker_id=worker_id))[
        "id"
    ] == 1
    assert (await connector.fetch_job_one(queues=["marsupilami"], worker_id=worker_id))[
        "id"
    ] == 5


async def test_fetch_job_one_prioritized(connector, worker_id):
    # This one will be selected second as it has a lower priority
    await connector.defer_job_one(
        task_name="mytask",
        priority=5,
        args={},
        queue="marsupilami",
        scheduled_at=None,
        lock=None,
        queueing_lock=None,
    )

    # This one will be selected first as it has a higher priority
    await connector.defer_job_one(
        task_name="mytask",
        priority=7,
        args={},
        queue="marsupilami",
        scheduled_at=None,
        lock=None,
        queueing_lock=None,
    )

    assert (await connector.fetch_job_one(queues=None, worker_id=worker_id))["id"] == 2
    assert (await connector.fetch_job_one(queues=None, worker_id=worker_id))["id"] == 1


async def test_fetch_job_one_none_lock(connector, worker_id):
    """Testing that 2 jobs with locks "None" don't block one another"""
    await connector.defer_job_one(
        task_name="mytask",
        priority=0,
        args={},
        queue="default",
        scheduled_at=None,
        lock=None,
        queueing_lock=None,
    )
    await connector.defer_job_one(
        task_name="mytask",
        priority=0,
        args={},
        queue="default",
        scheduled_at=None,
        lock=None,
        queueing_lock=None,
    )

    assert (await connector.fetch_job_one(queues=None, worker_id=worker_id))["id"] == 1
    assert (await connector.fetch_job_one(queues=None, worker_id=worker_id))["id"] == 2


async def test_finish_job_run(connector, worker_id):
    await connector.defer_job_one(
        task_name="mytask",
        priority=0,
        args={},
        queue="marsupilami",
        scheduled_at=None,
        lock="sher",
        queueing_lock="houba",
    )
    job_row = await connector.fetch_job_one(queues=None, worker_id=worker_id)
    id = job_row["id"]

    await connector.finish_job_run(job_id=id, status="finished", delete_job=False)

    assert connector.jobs[id]["attempts"] == 1
    assert connector.jobs[id]["status"] == "finished"


async def test_retry_job_run(connector, worker_id):
    await connector.defer_job_one(
        task_name="mytask",
        priority=0,
        args={},
        queue="marsupilami",
        scheduled_at=None,
        lock="sher",
        queueing_lock="houba",
    )
    job_row = await connector.fetch_job_one(queues=None, worker_id=worker_id)
    id = job_row["id"]

    retry_at = conftest.aware_datetime(2000, 1, 1)
    await connector.retry_job_run(
        job_id=id,
        retry_at=retry_at,
        new_priority=3,
        new_queue_name="some_queue",
        new_lock="some_lock",
    )

    assert connector.jobs[id]["attempts"] == 1
    assert connector.jobs[id]["status"] == "todo"
    assert connector.jobs[id]["scheduled_at"] == retry_at
    assert connector.jobs[id]["priority"] == 3
    assert connector.jobs[id]["queue_name"] == "some_queue"
    assert connector.jobs[id]["lock"] == "some_lock"
    assert len(connector.events[id]) == 4


async def test_apply_schema_run(connector):
    # If we don't crash, it's enough
    await connector.apply_schema_run()


async def test_listen_for_jobs_run(connector):
    # If we don't crash, it's enough
    await connector.listen_for_jobs_run()


async def test_defer_no_notify(connector):
    # This test is there to check that if the deferred queue doesn't match the
    # listened queue, the testing connector doesn't notify.

    event = asyncio.Event()

    async def on_notification(*, channel: str, payload: str):
        event.set()

    await connector.listen_notify(
        on_notification=on_notification, channels="some_other_channel"
    )
    await connector.defer_job_one(
        task_name="foo",
        priority=0,
        lock="bar",
        args={},
        scheduled_at=None,
        queue="baz",
        queueing_lock="houba",
    )

    assert not event.is_set()


async def test_update_heartbeat_run(connector, worker_id):
    connector.heartbeats = {}
    await connector.update_heartbeat_run(worker_id=worker_id)
    assert connector.heartbeats[worker_id] is not None


async def test_delete_finished_worker(connector, worker_id):
    connector.heartbeats = {worker_id: conftest.aware_datetime(2000, 1, 1)}
    await connector.delete_finished_worker_run(worker_id=worker_id)
    assert connector.heartbeats == {}


async def test_prune_stalled_workers_run(connector):
    connector.heartbeats = {
        "worker1": conftest.aware_datetime(2000, 1, 1),
        "worker2": conftest.aware_datetime(2000, 1, 1),
        "worker3": conftest.aware_datetime(2100, 1, 1),
    }
    await connector.prune_stalled_workers_run(seconds_since_heartbeat=0)
    assert connector.heartbeats == {"worker3": conftest.aware_datetime(2100, 1, 1)}
