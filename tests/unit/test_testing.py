import pendulum


def test_reset(job_store):
    job_store.jobs = {1: {}}
    job_store.reset()
    assert job_store.jobs == {}


def test_generic_execute(job_store):
    result = {}
    job_store.reverse_queries = {"a": "b"}

    def b(**kwargs):
        result.update(kwargs)

    job_store.b_youpi = b

    job_store.generic_execute("a", "youpi", i="j")

    assert result == {"i": "j"}


def test_execute_query(job_store, mocker):
    job_store.generic_execute = mocker.Mock()
    job_store.execute_query("a", b="c")
    job_store.generic_execute.assert_called_with("a", "run", b="c")


def test_execute_query_one(job_store, mocker):
    job_store.generic_execute = mocker.Mock()
    assert (
        job_store.execute_query_one("a", b="c")
        == job_store.generic_execute.return_value
    )
    job_store.generic_execute.assert_called_with("a", "one", b="c")


def test_execute_query_all(job_store, mocker):
    job_store.generic_execute = mocker.Mock()
    assert (
        job_store.execute_query_all("a", b="c")
        == job_store.generic_execute.return_value
    )
    job_store.generic_execute.assert_called_with("a", "all", b="c")


def test_make_dynamic_query(job_store):
    assert job_store.make_dynamic_query("foo {bar}", bar="baz") == "foo baz"


def test_defer_job_one(job_store):
    job = job_store.defer_job_one(
        task_name="mytask",
        lock="sher",
        args={"a": "b"},
        scheduled_at=None,
        queue="marsupilami",
    )

    assert job_store.jobs == {
        1: {
            "id": 1,
            "queue_name": "marsupilami",
            "task_name": "mytask",
            "lock": "sher",
            "args": {"a": "b"},
            "status": "todo",
            "scheduled_at": None,
            "started_at": None,
            "attempts": 0,
        }
    }
    assert job_store.jobs[1] == job


def test_current_locks(job_store):
    job_store.jobs = {
        1: {"status": "todo", "lock": "foo"},
        2: {"status": "doing", "lock": "yay"},
    }
    assert job_store.current_locks == {"yay"}


def test_finished_jobs(job_store):
    job_store.jobs = {
        1: {"status": "todo"},
        2: {"status": "doing"},
        3: {"status": "succeeded"},
        4: {"status": "failed"},
    }
    assert job_store.finished_jobs == [{"status": "succeeded"}, {"status": "failed"}]


def test_select_stalled_jobs_all(job_store):
    job_store.jobs = {
        # We're not selecting this job because it's "succeeded"
        1: {
            "id": 1,
            "status": "succeeded",
            "started_at": pendulum.datetime(2000, 1, 1),
            "queue_name": "marsupilami",
            "task_name": "mytask",
        },
        # This one because it's the wrong queue
        2: {
            "id": 2,
            "status": "doing",
            "started_at": pendulum.datetime(2000, 1, 1),
            "queue_name": "other_queue",
            "task_name": "mytask",
        },
        # This one because of the task
        3: {
            "id": 3,
            "status": "doing",
            "started_at": pendulum.datetime(2000, 1, 1),
            "queue_name": "marsupilami",
            "task_name": "my_other_task",
        },
        # This one because  it's not stalled
        4: {
            "id": 4,
            "status": "doing",
            "started_at": pendulum.datetime(2100, 1, 1),
            "queue_name": "marsupilami",
            "task_name": "mytask",
        },
        # We're taking this one.
        5: {
            "id": 5,
            "status": "doing",
            "started_at": pendulum.datetime(2000, 1, 1),
            "queue_name": "marsupilami",
            "task_name": "mytask",
        },
        # And this one
        6: {
            "id": 6,
            "status": "doing",
            "started_at": pendulum.datetime(2000, 1, 1),
            "queue_name": "marsupilami",
            "task_name": "mytask",
        },
    }

    results = job_store.select_stalled_jobs_all(
        queue="marsupilami", task_name="mytask", nb_seconds=0
    )
    assert [job["id"] for job in results] == [5, 6]


def test_delete_old_jobs_run(job_store):
    job_store.jobs = {
        # We're not deleting this job because it's "doing"
        1: {"id": 1, "status": "doing", "queue_name": "marsupilami"},
        # This one because it's the wrong queue
        2: {"id": 2, "status": "succeeded", "queue_name": "other_queue"},
        # This one is not old enough
        3: {"id": 3, "status": "succeeded", "queue_name": "marsupilami"},
        # This one we delete
        4: {"id": 4, "status": "succeeded", "queue_name": "marsupilami"},
    }
    job_store.events = {
        1: [{"type": "succeeded", "at": pendulum.datetime(2000, 1, 1)}],
        2: [{"type": "succeeded", "at": pendulum.datetime(2000, 1, 1)}],
        3: [{"type": "succeeded", "at": pendulum.now()}],
        4: [{"type": "succeeded", "at": pendulum.datetime(2000, 1, 1)}],
    }

    job_store.delete_old_jobs_run(
        queue="marsupilami", statuses=("succeeded"), nb_hours=0
    )
    assert 4 not in job_store.jobs


def test_fetch_job_one(job_store):
    # This one will be selected, then skipped the second time because it's processing
    job_store.defer_job_one(
        task_name="mytask", args={}, queue="marsupilami", scheduled_at=None, lock="a"
    )

    # This one because it's the wrong queue
    job_store.defer_job_one(
        task_name="mytask", args={}, queue="other_queue", scheduled_at=None, lock="b"
    )
    # This one because of the scheduled_at
    job_store.defer_job_one(
        task_name="mytask",
        args={},
        queue="marsupilami",
        scheduled_at=pendulum.datetime(2100, 1, 1),
        lock="c",
    )
    # This one because of the lock
    job_store.defer_job_one(
        task_name="mytask", args={}, queue="marsupilami", scheduled_at=None, lock="a"
    )
    # We're taking this one.
    job_store.defer_job_one(
        task_name="mytask", args={}, queue="marsupilami", scheduled_at=None, lock="e"
    )

    assert job_store.fetch_job_one(queues=["marsupilami"])["id"] == 1
    assert job_store.fetch_job_one(queues=["marsupilami"])["id"] == 5


def test_finish_job_run(job_store):
    job_store.defer_job_one(
        task_name="mytask", args={}, queue="marsupilami", scheduled_at=None, lock="sher"
    )
    job_row = job_store.fetch_job_one(queues=None)
    id = job_row["id"]

    job_store.finish_job_run(job_id=id, status="finished")

    assert job_store.jobs[id]["attempts"] == 0
    assert job_store.jobs[id]["status"] == "finished"
    assert job_store.jobs[id]["scheduled_at"] is None


def test_finish_job_run_retry(job_store):
    job_store.defer_job_one(
        task_name="mytask", args={}, queue="marsupilami", scheduled_at=None, lock="sher"
    )
    job_row = job_store.fetch_job_one(queues=None)
    id = job_row["id"]

    retry_at = pendulum.datetime(2000, 1, 1)
    job_store.finish_job_run(job_id=id, status="todo", scheduled_at=retry_at)

    assert job_store.jobs[id]["attempts"] == 1
    assert job_store.jobs[id]["status"] == "todo"
    assert job_store.jobs[id]["scheduled_at"] == retry_at
    assert len(job_store.events[id]) == 4


def test_finish_job_run_retry_no_schedule(job_store):
    job_store.defer_job_one(
        task_name="mytask", args={}, queue="marsupilami", scheduled_at=None, lock="sher"
    )
    job_row = job_store.fetch_job_one(queues=None)
    id = job_row["id"]

    job_store.finish_job_run(job_id=id, status="todo", scheduled_at=None)

    assert job_store.jobs[id]["attempts"] == 1
    assert job_store.jobs[id]["status"] == "todo"
    assert job_store.jobs[id]["scheduled_at"] is None
    assert len(job_store.events[id]) == 3


def test_listen_for_jobs_run(job_store):
    # If we don't crash, it's enough
    job_store.listen_for_jobs(queues=["a", "b"])


def test_wait_for_jobs(job_store):
    # If we don't crash, it's enough
    job_store.wait_for_jobs()


def test_migrate_run(job_store):
    # If we don't crash, it's enough
    job_store.migrate_run()


def test_stop(job_store):
    # If we don't crash, it's enough
    job_store.stop()
