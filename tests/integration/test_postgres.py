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


@pytest.fixture()
def get_all(connection):
    def f(table, *fields):
        with connection.cursor(cursor_factory=postgres.RealDictCursor) as cursor:
            cursor.execute(f"SELECT {', '.join(fields)} FROM {table}")
            return list(iter(cursor.fetchone, None))

    return f


def test_launch_task(connection, get_all):
    queue = "marsupilami"
    postgres.register_queue(connection, queue)
    pk = postgres.launch_task(
        connection, queue=queue, name="bob", lock="sher", kwargs={"a": 1, "b": 2}
    )

    result = get_all("tasks", "id", "args", "status", "targeted_object", "task_type")
    assert result == [
        {
            "id": pk,
            "args": {"a": 1, "b": 2},
            "status": "todo",
            "targeted_object": "sher",
            "task_type": "bob",
        }
    ]


def test_launch_task_no_queue(connection):
    queue = "marsupilami"
    with pytest.raises(exceptions.QueueNotFound):
        postgres.launch_task(
            connection, queue=queue, name="bob", lock="sher", kwargs={"a": 1, "b": 2}
        )


def test_get_tasks(connection):
    postgres.register_queue(connection, "queue_a")
    postgres.register_queue(connection, "queue_b")
    postgres.launch_task(connection, "queue_a", "task_1", "lock_1", {"a": "b"})
    # We won't see this one because of the lock
    postgres.launch_task(connection, "queue_a", "task_2", "lock_1", {"c": "d"})
    postgres.launch_task(connection, "queue_a", "task_3", "lock_2", {"e": "f"})
    # We won't see this one because of the queue
    postgres.launch_task(connection, "queue_b", "task_4", "lock_3", {"g": "h"})

    result = list(postgres.get_tasks(connection, "queue_a"))

    t1, t2 = result
    assert result == [
        jobs.Job(
            id=t1.id,
            kwargs={"a": "b"},
            lock="lock_1",
            task_name="task_1",
            queue="queue_a",
        ),
        jobs.Job(
            id=t2.id,
            kwargs={"e": "f"},
            lock="lock_2",
            task_name="task_3",
            queue="queue_a",
        ),
    ]


def test_finish_task(get_all, connection):
    postgres.register_queue(connection, "queue_a")
    postgres.launch_task(connection, "queue_a", "task_1", "lock_1", {"a": "b"})
    task = next(postgres.get_tasks(connection, "queue_a"))

    assert get_all("tasks", "status") == [{"status": "doing"}]

    postgres.finish_task(connection, task_id=task.id, status="done")

    assert get_all("tasks", "status") == [{"status": "done"}]


def test_register_queue(connection, get_all):
    pk = postgres.register_queue(connection, "marsupilami")

    result = get_all("queues", "*")
    assert result == [{"id": pk, "queue_name": "marsupilami"}]


def test_register_queue_conflict(connection, get_all):
    postgres.register_queue(connection, "marsupilami")

    pk = postgres.register_queue(connection, "marsupilami")

    assert pk is None
    result = get_all("queues", "queue_name")
    assert result == [{"queue_name": "marsupilami"}]


def test_listen_queue(connection):
    queue = random.choices(string.ascii_letters, k=10)
    queue_full_name = f"queue#{queue}"
    postgres.listen_queue(connection, queue)
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
            ("task_status",),
        )

        pg_values = {row[0] for row in cursor.fetchall()}
        python_values = {status.value for status in jobs.Status.__members__.values()}
        assert pg_values == python_values


def test_wait_for_jobs(connection):
    postgres.register_queue(connection=connection, queue="yay")
    postgres.listen_queue(connection=connection, queue="yay")

    def stop():
        time.sleep(0.5)
        postgres.launch_task(
            connection=connection, queue="yay", name="oh", lock="sher", kwargs={}
        )

    thread = threading.Thread(target=stop)
    thread.start()

    before = time.perf_counter()
    postgres.wait_for_jobs(connection=connection, timeout=3)
    after = time.perf_counter()

    # If we wait less than 1 sec, it means the wait didn't reach the timeout.
    assert after - before < 1
