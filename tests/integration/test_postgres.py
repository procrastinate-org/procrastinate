import random
import string

import psycopg2
import pytest

from cabbage import exceptions, postgres


def test_init_pg_extensions():
    postgres.init_pg_extensions()
    json = psycopg2.extensions.adapt({"hello": ["world", 42]})

    assert type(json).__name__ == "Json"


@pytest.fixture()
def get_all(db):
    def f(table, *fields):
        with postgres.get_dict_cursor(db) as cursor:
            cursor.execute(f"SELECT {', '.join(fields)} FROM {table}")
            return list(iter(cursor.fetchone, None))

    return f


def test_launch_task(get_all):
    queue = "marsupilami"
    postgres.register_queue(queue)
    pk = postgres.launch_task(
        queue=queue, name="bob", lock="sher", kwargs={"a": 1, "b": 2}
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


def test_launch_task_no_queue(db):
    queue = "marsupilami"
    with pytest.raises(exceptions.QueueNotFound):
        postgres.launch_task(
            queue=queue, name="bob", lock="sher", kwargs={"a": 1, "b": 2}
        )


def test_get_tasks(db):
    postgres.register_queue("queue_a")
    postgres.register_queue("queue_b")
    postgres.launch_task("queue_a", "task_1", "lock_1", {"a": "b"})
    # We won't see this one because of the lock
    postgres.launch_task("queue_a", "task_2", "lock_1", {"c": "d"})
    postgres.launch_task("queue_a", "task_3", "lock_2", {"e": "f"})
    # We won't see this one because of the queue
    postgres.launch_task("queue_b", "task_4", "lock_3", {"g": "h"})

    with postgres.get_dict_cursor(db) as cursor:
        result = list(postgres.get_tasks(cursor, "queue_a"))

    t1, t2 = result
    assert result == [
        postgres.TaskRow(
            id=t1.id, args={"a": "b"}, targeted_object="lock_1", task_type="task_1"
        ),
        postgres.TaskRow(
            id=t2.id, args={"e": "f"}, targeted_object="lock_2", task_type="task_3"
        ),
    ]


def test_finish_task(get_all, db):
    postgres.register_queue("queue_a")
    postgres.launch_task("queue_a", "task_1", "lock_1", {"a": "b"})
    with postgres.get_dict_cursor(db) as cursor:
        task = next(postgres.get_tasks(cursor, "queue_a"))

        assert get_all("tasks", "status") == [{"status": "doing"}]

        postgres.finish_task(cursor=cursor, task_id=task.id, status="done")

    assert get_all("tasks", "status") == [{"status": "done"}]


def test_register_queue(get_all):
    pk = postgres.register_queue("marsupilami")

    result = get_all("queues", "*")
    assert result == [{"id": pk, "queue_name": "marsupilami"}]


def test_register_queue_conflict(get_all):
    postgres.register_queue("marsupilami")

    pk = postgres.register_queue("marsupilami")

    assert pk is None
    result = get_all("queues", "queue_name")
    assert result == [{"queue_name": "marsupilami"}]


def test_listen_queue(db):
    with db.cursor() as cursor:
        queue = random.choices(string.ascii_letters, k=10)
        queue_full_name = f"queue#{queue}"
        postgres.listen_queue(curs=cursor, queue=queue)
        db.commit()
        cursor.execute(
            """SELECT COUNT(*) FROM pg_listening_channels()
                          WHERE pg_listening_channels = %s""",
            (queue_full_name,),
        )
        assert cursor.fetchone()[0] == 1


def test_get_global_connection(db):  # pylint: disable=unused-argument
    postgres.reset_global_connection()
    a = postgres.get_global_connection(dbname="cabbage_test")
    b = postgres.get_global_connection(dbname="cabbage_test")

    assert a is b
    assert isinstance(a, psycopg2.extensions.connection)


def test_reset_global_connection(db):  # pylint: disable=unused-argument
    postgres.get_global_connection(dbname="cabbage_test")
    postgres.reset_global_connection()

    assert postgres._connection is None


def test_get_dict_cursor(db):
    with postgres.get_dict_cursor(db) as cursor:
        cursor.execute("SELECT TRUE")

        assert cursor.fetchone() == {"bool": True}
