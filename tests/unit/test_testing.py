import asyncio

import pytest

from procrastinate import utils

from .. import conftest


def test_reset(connector):
    connector.jobs = {1: {}}
    connector.reset()
    assert connector.jobs == {}


def test_generic_execute(connector):
    result = {}
    connector.reverse_queries = {"a": "b"}

    def b(**kwargs):
        result.update(kwargs)

    connector.b_youpi = b

    connector.generic_execute("a", "youpi", i="j")

    assert result == {"i": "j"}


@pytest.mark.asyncio
async def test_execute_query(connector, mocker):
    connector.generic_execute = mocker.Mock()
    await connector.execute_query_async("a", b="c")
    connector.generic_execute.assert_called_with("a", "run", b="c")


@pytest.mark.asyncio
async def test_execute_query_one(connector, mocker):
    connector.generic_execute = mocker.Mock()
    assert (
        await connector.execute_query_one_async("a", b="c")
        == connector.generic_execute.return_value
    )
    connector.generic_execute.assert_called_with("a", "one", b="c")


@pytest.mark.asyncio
async def test_execute_query_all_async(connector, mocker):
    connector.generic_execute = mocker.Mock()
    assert (
        await connector.execute_query_all_async("a", b="c")
        == connector.generic_execute.return_value
    )
    connector.generic_execute.assert_called_with("a", "all", b="c")


def test_make_dynamic_query(connector):
    assert connector.make_dynamic_query("foo {bar}", bar="baz") == "foo baz"


def test_defer_job_one(connector):
    job = connector.defer_job_one(
        task_name="mytask",
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
            "task_name": "mytask",
            "lock": "sher",
            "queueing_lock": "houba",
            "args": {"a": "b"},
            "status": "todo",
            "scheduled_at": None,
            "attempts": 0,
        }
    }
    assert connector.jobs[1] == job


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


def test_select_stalled_jobs_all(connector):
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

    results = connector.select_stalled_jobs_all(
        queue="marsupilami", task_name="mytask", nb_seconds=0
    )
    assert [job["id"] for job in results] == [5, 6]


def test_delete_old_jobs_run(connector):
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

    connector.delete_old_jobs_run(
        queue="marsupilami", statuses=("succeeded"), nb_hours=0
    )
    assert 4 not in connector.jobs


def test_fetch_job_one(connector):
    # This one will be selected, then skipped the second time because it's processing
    connector.defer_job_one(
        task_name="mytask",
        args={},
        queue="marsupilami",
        scheduled_at=None,
        lock="a",
        queueing_lock="a",
    )

    # This one because it's the wrong queue
    connector.defer_job_one(
        task_name="mytask",
        args={},
        queue="other_queue",
        scheduled_at=None,
        lock="b",
        queueing_lock="b",
    )
    # This one because of the scheduled_at
    connector.defer_job_one(
        task_name="mytask",
        args={},
        queue="marsupilami",
        scheduled_at=conftest.aware_datetime(2100, 1, 1),
        lock="c",
        queueing_lock="c",
    )
    # This one because of the lock
    connector.defer_job_one(
        task_name="mytask",
        args={},
        queue="marsupilami",
        scheduled_at=None,
        lock="a",
        queueing_lock="d",
    )
    # We're taking this one.
    connector.defer_job_one(
        task_name="mytask",
        args={},
        queue="marsupilami",
        scheduled_at=None,
        lock="e",
        queueing_lock="e",
    )

    assert connector.fetch_job_one(queues=["marsupilami"])["id"] == 1
    assert connector.fetch_job_one(queues=["marsupilami"])["id"] == 5


def test_finish_job_run(connector):
    connector.defer_job_one(
        task_name="mytask",
        args={},
        queue="marsupilami",
        scheduled_at=None,
        lock="sher",
        queueing_lock="houba",
    )
    job_row = connector.fetch_job_one(queues=None)
    id = job_row["id"]

    connector.finish_job_run(job_id=id, status="finished")

    assert connector.jobs[id]["attempts"] == 0
    assert connector.jobs[id]["status"] == "finished"
    assert connector.jobs[id]["scheduled_at"] is None


def test_finish_job_run_retry(connector):
    connector.defer_job_one(
        task_name="mytask",
        args={},
        queue="marsupilami",
        scheduled_at=None,
        lock="sher",
        queueing_lock="houba",
    )
    job_row = connector.fetch_job_one(queues=None)
    id = job_row["id"]

    retry_at = conftest.aware_datetime(2000, 1, 1)
    connector.finish_job_run(job_id=id, status="todo", scheduled_at=retry_at)

    assert connector.jobs[id]["attempts"] == 1
    assert connector.jobs[id]["status"] == "todo"
    assert connector.jobs[id]["scheduled_at"] == retry_at
    assert len(connector.events[id]) == 4


def test_finish_job_run_retry_no_schedule(connector):
    connector.defer_job_one(
        task_name="mytask",
        args={},
        queue="marsupilami",
        scheduled_at=None,
        lock="sher",
        queueing_lock="houba",
    )
    job_row = connector.fetch_job_one(queues=None)
    id = job_row["id"]

    connector.finish_job_run(job_id=id, status="todo", scheduled_at=None)

    assert connector.jobs[id]["attempts"] == 1
    assert connector.jobs[id]["status"] == "todo"
    assert connector.jobs[id]["scheduled_at"] is None
    assert len(connector.events[id]) == 3


def test_apply_schema_run(connector):
    # If we don't crash, it's enough
    connector.apply_schema_run()


def test_listen_for_jobs_run(connector):
    # If we don't crash, it's enough
    connector.listen_for_jobs_run()


@pytest.mark.asyncio
async def test_defer_no_notify(connector):
    # This test is there to check that if the deferred queue doesn't match the
    # listened queue, the testing connector doesn't notify.
    event = asyncio.Event()
    await connector.listen_notify(event=event, channels="some_other_channel")
    connector.defer_job_one(
        task_name="foo",
        lock="bar",
        args={},
        scheduled_at=None,
        queue="baz",
        queueing_lock="houba",
    )

    assert not event.is_set()
