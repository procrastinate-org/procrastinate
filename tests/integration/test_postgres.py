import datetime
import random
import string
import threading
import time

import pendulum
import psycopg2
import pytest

from cabbage import jobs, postgres


def test_init_pg_extensions():
    postgres.init_pg_extensions()
    json = psycopg2.extensions.adapt({"hello": ["world", 42]})

    assert type(json).__name__ == "Json"


def test_get_connection(connection):
    dsn = connection.get_dsn_parameters()

    new_connection = postgres.get_connection(**dsn)

    assert new_connection.get_dsn_parameters() == dsn


@pytest.fixture
def get_all(connection):
    def f(table, *fields):
        with connection.cursor(cursor_factory=postgres.RealDictCursor) as cursor:
            cursor.execute(f"SELECT {', '.join(fields)} FROM {table}")
            return list(iter(cursor.fetchone, None))

    return f


def test_launch_job(pg_job_store, get_all):
    queue = "marsupilami"
    job = jobs.Job(
        id=0,
        queue=queue,
        task_name="bob",
        lock="sher",
        task_kwargs={"a": 1, "b": 2},
        job_store=pg_job_store,
    )
    pk = pg_job_store.launch_job(job=job)

    result = get_all("cabbage_jobs", "id", "args", "status", "lock", "task_name")
    assert result == [
        {
            "id": pk,
            "args": {"a": 1, "b": 2},
            "status": "todo",
            "lock": "sher",
            "task_name": "bob",
        }
    ]


def test_get_jobs(pg_job_store):
    pg_job_store.launch_job(
        jobs.Job(
            id=0,
            queue="queue_a",
            task_name="task_1",
            lock="lock_1",
            task_kwargs={"a": "b"},
            job_store=pg_job_store,
        )
    )
    # We won't see this one because of the lock
    pg_job_store.launch_job(
        jobs.Job(
            id=0,
            queue="queue_a",
            task_name="task_2",
            lock="lock_1",
            task_kwargs={"c": "d"},
            job_store=pg_job_store,
        )
    )
    pg_job_store.launch_job(
        jobs.Job(
            id=0,
            queue="queue_a",
            task_name="task_3",
            lock="lock_2",
            task_kwargs={"e": "f"},
            job_store=pg_job_store,
        )
    )
    # We won't see this one because of the queue
    pg_job_store.launch_job(
        jobs.Job(
            id=0,
            queue="queue_b",
            task_name="task_4",
            lock="lock_3",
            task_kwargs={"g": "h"},
            job_store=pg_job_store,
        )
    )
    pg_job_store.launch_job(
        jobs.Job(
            id=0,
            queue="queue_a",
            task_name="task_5",
            lock="lock_5",
            task_kwargs={"i": "j"},
            scheduled_at=pendulum.datetime(2000, 1, 1),
            job_store=pg_job_store,
        )
    )
    # We won't see this one because of the scheduled date
    pg_job_store.launch_job(
        jobs.Job(
            id=0,
            queue="queue_a",
            task_name="task_6",
            lock="lock_6",
            task_kwargs={"k": "l"},
            scheduled_at=pendulum.datetime(2050, 1, 1),
            job_store=pg_job_store,
        )
    )

    result = list(pg_job_store.get_jobs(queues=["queue_a"]))

    t1, t2, t3 = result
    assert result == [
        jobs.Job(
            id=t1.id,
            task_kwargs={"a": "b"},
            lock="lock_1",
            task_name="task_1",
            queue="queue_a",
            job_store=pg_job_store,
        ),
        jobs.Job(
            id=t2.id,
            task_kwargs={"e": "f"},
            lock="lock_2",
            task_name="task_3",
            queue="queue_a",
            job_store=pg_job_store,
        ),
        jobs.Job(
            id=t3.id,
            queue="queue_a",
            task_name="task_5",
            lock="lock_5",
            task_kwargs={"i": "j"},
            scheduled_at=pendulum.datetime(2000, 1, 1),
            job_store=pg_job_store,
        ),
    ]


def test_get_stalled_jobs(get_all, pg_job_store):
    pg_job_store.launch_job(
        jobs.Job(
            id=0,
            queue="queue_a",
            task_name="task_1",
            lock="lock_1",
            task_kwargs={"a": "b"},
            job_store=pg_job_store,
        )
    )
    job_id = list(get_all("cabbage_jobs", "id"))[0]["id"]

    # No started job
    assert list(pg_job_store.get_stalled_jobs(nb_seconds=3600)) == []

    # We start a job and fake its `started_at`
    job = next(pg_job_store.get_jobs(queues=["queue_a"]))
    with pg_job_store.connection.cursor() as cursor:
        cursor.execute(
            f"UPDATE cabbage_jobs SET started_at=NOW() - INTERVAL '30 minutes' "
            f"WHERE id={job_id}"
        )

    # Nb_seconds parameter
    assert list(pg_job_store.get_stalled_jobs(nb_seconds=3600)) == []
    assert list(pg_job_store.get_stalled_jobs(nb_seconds=1800)) == [job]

    # Queue parameter
    assert list(pg_job_store.get_stalled_jobs(nb_seconds=1800, queue="queue_a")) == [
        job
    ]
    assert list(pg_job_store.get_stalled_jobs(nb_seconds=1800, queue="queue_b")) == []
    # Task name parameter
    assert list(pg_job_store.get_stalled_jobs(nb_seconds=1800, task_name="task_1")) == [
        job
    ]
    assert (
        list(pg_job_store.get_stalled_jobs(nb_seconds=1800, task_name="task_2")) == []
    )


def test_finish_job(get_all, pg_job_store):
    pg_job_store.launch_job(
        jobs.Job(
            id=0,
            queue="queue_a",
            task_name="task_1",
            lock="lock_1",
            task_kwargs={"a": "b"},
            job_store=pg_job_store,
        )
    )
    job = next(pg_job_store.get_jobs(queues=["queue_a"]))

    assert get_all("cabbage_jobs", "status") == [{"status": "doing"}]
    started_at = get_all("cabbage_jobs", "started_at")[0]["started_at"]
    assert started_at.date() == datetime.datetime.utcnow().date()
    assert get_all("cabbage_jobs", "attempts") == [{"attempts": 0}]

    pg_job_store.finish_job(job=job, status=jobs.Status.DONE)

    expected = [{"status": "done", "started_at": started_at, "attempts": 1}]
    assert get_all("cabbage_jobs", "status", "started_at", "attempts") == expected


def test_listen_queue(pg_job_store):
    queue = "".join(random.choices(string.ascii_letters, k=10))
    queue_full_name = f"cabbage_queue#{queue}"
    pg_job_store.listen_for_jobs(queues=[queue])
    pg_job_store.connection.commit()

    with pg_job_store.connection.cursor() as cursor:
        cursor.execute(
            """SELECT COUNT(*) FROM pg_listening_channels()
                          WHERE pg_listening_channels = %s""",
            (queue_full_name,),
        )
        assert cursor.fetchone()[0] == 1


def test_listen_all_queue(pg_job_store, connection):
    pg_job_store.listen_for_jobs()
    pg_job_store.connection.commit()

    with pg_job_store.connection.cursor() as cursor:
        cursor.execute(
            """SELECT COUNT(*) FROM pg_listening_channels()
                          WHERE pg_listening_channels = 'cabbage_any_queue'"""
        )
        assert cursor.fetchone()[0] == 1


def test_enum_synced(connection):
    # If this test breaks, it means you've changed either the task_status PG enum
    # or the python cabbage.jobs.Status Enum without updating the other.
    with connection.cursor() as cursor:
        cursor.execute(
            """SELECT e.enumlabel FROM pg_enum e
               JOIN pg_type t ON e.enumtypid = t.oid WHERE t.typname = %s""",
            ("cabbage_job_status",),
        )

        pg_values = {row[0] for row in cursor.fetchall()}
        python_values = {status.value for status in jobs.Status.__members__.values()}
        assert pg_values == python_values


def test_wait_for_jobs(pg_job_store, connection_params):

    pg_job_store.socket_timeout = 3
    pg_job_store.listen_for_jobs()

    def stop():
        try:
            inner_job_store = postgres.PostgresJobStore(**connection_params)

            time.sleep(0.5)
            inner_job_store.launch_job(
                jobs.Job(
                    id=0,
                    queue="yay",
                    task_name="oh",
                    lock="sher",
                    task_kwargs={},
                    job_store=inner_job_store,
                )
            )
        finally:
            inner_job_store.connection.close()

    thread = threading.Thread(target=stop)
    thread.start()

    before = time.perf_counter()
    pg_job_store.wait_for_jobs()
    after = time.perf_counter()

    # If we wait less than 1 sec, it means the wait didn't reach the timeout.
    assert after - before < 1
