from typing import Any, Iterator, NamedTuple

import psycopg2
from psycopg2 import extras, sql
from psycopg2.extras import RealDictCursor

from cabbage import exceptions, types


class TaskRow(NamedTuple):
    id: int
    task_type: str
    args: types.JSONDict
    targeted_object: str


def init_pg_extensions() -> None:
    psycopg2.extensions.register_adapter(dict, extras.Json)


def launch_task(queue: str, name: str, lock: str, kwargs: types.JSONDict) -> int:

    conn = get_global_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            """INSERT INTO tasks (queue_id, task_type, targeted_object, args)
               SELECT id, %s, %s, %s FROM queues WHERE queue_name=%s
               RETURNING id;""",
            (name, lock, kwargs, queue),
        )
        row = cursor.fetchone()

    if not row:
        raise exceptions.QueueNotFound(queue)

    conn.commit()
    return row[0]


def get_tasks(cursor: Any, queue: str) -> Iterator[TaskRow]:
    while True:
        cursor.execute(
            """SELECT id, args, targeted_object, task_type FROM fetch_task(%s);""",
            (queue,),
        )
        cursor.connection.commit()

        row = cursor.fetchone()

        # fetch_tasks will always return a row, but is there's no relevant
        # value, it will all be None
        if row["id"] is None:
            return

        yield TaskRow(**row)


def finish_task(cursor: Any, task_id: int, status: str) -> None:
    cursor.execute("""SELECT finish_task(%s, %s);""", (task_id, status))
    cursor.connection.commit()


def register_queue(queue: str) -> None:
    conn = get_global_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            """INSERT INTO queues (queue_name)
               VALUES (%s)
               ON CONFLICT DO NOTHING
               RETURNING id
               """,
            (queue,),
        )
        row = cursor.fetchone()

    conn.commit()
    return row[0] if row else None


def listen_queue(curs: Any, queue: str) -> None:
    queue_name = sql.Identifier(f"queue#{queue}")
    curs.execute(sql.SQL("""LISTEN {queue_name};""").format(queue_name=queue_name))


def get_global_connection(**kwargs: Any) -> Any:
    global _connection  # pylint: disable=global-statement
    if _connection is None:
        _connection = psycopg2.connect("", **kwargs)
    return _connection


def reset_global_connection() -> None:
    global _connection  # pylint: disable=global-statement
    _connection = None


def get_dict_cursor(conn: Any) -> Any:
    return conn.cursor(cursor_factory=RealDictCursor)


init_pg_extensions()
_connection = None
