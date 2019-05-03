import random
import string
import threading
import time

import psycopg2
import pytest

from cabbage import exceptions, jobs, postgres


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


@pytest.fixture
def job_store(connection):
    return postgres.PostgresJobStore(connection=connection)


def test_launch_job(job_store, get_all):
    queue = "marsupilami"
    job_store.register_queue(queue)
    job = jobs.Job(
        id=0,
        queue=queue,
        task_name="bob",
        lock="sher",
        task_kwargs={"a": 1, "b": 2},
        job_store=job_store,
    )
    pk = job_store.launch_job(job=job)

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


def test_launch_job_no_queue(job_store):
    queue = "marsupilami"
    job = jobs.Job(
        id=0,
        queue=queue,
        task_name="bob",
        lock="sher",
        task_kwargs={"a": 1, "b": 2},
        job_store=job_store,
    )
    with pytest.raises(exceptions.QueueNotFound):
        job_store.launch_job(job=job)


def test_get_jobs(job_store):
    job_store.register_queue("queue_a")
    job_store.register_queue("queue_b")
    job_store.launch_job(
        jobs.Job(
            id=0,
            queue="queue_a",
            task_name="task_1",
            lock="lock_1",
            task_kwargs={"a": "b"},
            job_store=job_store,
        )
    )
    # We won't see this one because of the lock
    job_store.launch_job(
        jobs.Job(
            id=0,
            queue="queue_a",
            task_name="task_2",
            lock="lock_1",
            task_kwargs={"c": "d"},
            job_store=job_store,
        )
    )
    job_store.launch_job(
        jobs.Job(
            id=0,
            queue="queue_a",
            task_name="task_3",
            lock="lock_2",
            task_kwargs={"e": "f"},
            job_store=job_store,
        )
    )
    # We won't see this one because of the queue
    job_store.launch_job(
        jobs.Job(
            id=0,
            queue="queue_b",
            task_name="task_4",
            lock="lock_3",
            task_kwargs={"g": "h"},
            job_store=job_store,
        )
    )

    result = list(job_store.get_jobs("queue_a"))

    t1, t2 = result
    assert result == [
        jobs.Job(
            id=t1.id,
            task_kwargs={"a": "b"},
            lock="lock_1",
            task_name="task_1",
            queue="queue_a",
            job_store=job_store,
        ),
        jobs.Job(
            id=t2.id,
            task_kwargs={"e": "f"},
            lock="lock_2",
            task_name="task_3",
            queue="queue_a",
            job_store=job_store,
        ),
    ]


def test_finish_job(get_all, job_store):
    job_store.register_queue("queue_a")
    job_store.launch_job(
        jobs.Job(
            id=0,
            queue="queue_a",
            task_name="task_1",
            lock="lock_1",
            task_kwargs={"a": "b"},
            job_store=job_store,
        )
    )
    job = next(job_store.get_jobs("queue_a"))

    assert get_all("cabbage_jobs", "status") == [{"status": "doing"}]

    job_store.finish_job(job=job, status=jobs.Status.DONE)

    assert get_all("cabbage_jobs", "status") == [{"status": "done"}]


def test_register_queue(get_all, job_store):
    pk = job_store.register_queue("marsupilami")

    result = get_all("cabbage_queues", "*")
    assert result == [{"id": pk, "queue_name": "marsupilami"}]


def test_register_queue_conflict(get_all, job_store):
    job_store.register_queue("marsupilami")

    pk = job_store.register_queue("marsupilami")

    assert pk is None
    result = get_all("cabbage_queues", "queue_name")
    assert result == [{"queue_name": "marsupilami"}]


def test_listen_queue(job_store, connection):
    queue = "".join(random.choices(string.ascii_letters, k=10))
    queue_full_name = f"cabbage_queue#{queue}"
    job_store.listen_for_jobs(queue=queue)
    connection.commit()

    with connection.cursor() as cursor:
        cursor.execute(
            """SELECT COUNT(*) FROM pg_listening_channels()
                          WHERE pg_listening_channels = %s""",
            (queue_full_name,),
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


def test_wait_for_jobs(job_store):
    job_store.register_queue(queue="yay")
    job_store.listen_for_jobs(queue="yay")

    def stop():
        time.sleep(0.5)
        job_store.launch_job(
            jobs.Job(
                id=0,
                queue="yay",
                task_name="oh",
                lock="sher",
                task_kwargs={},
                job_store=job_store,
            )
        )

    thread = threading.Thread(target=stop)
    thread.start()

    before = time.perf_counter()
    job_store.wait_for_jobs(timeout=3)
    after = time.perf_counter()

    # If we wait less than 1 sec, it means the wait didn't reach the timeout.
    assert after - before < 1
