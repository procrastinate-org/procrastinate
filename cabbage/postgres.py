from typing import Iterator, NamedTuple, Optional

import psycopg2
from psycopg2 import extras, sql
from psycopg2.extras import RealDictCursor

from cabbage import exceptions, types


class TaskRow(NamedTuple):
    id: int
    task_type: str
    args: types.JSONDict
    targeted_object: str


def get_connection(**kwargs) -> psycopg2._psycopg.connection:
    return psycopg2.connect("", **kwargs)


def init_pg_extensions() -> None:
    psycopg2.extensions.register_adapter(dict, extras.Json)


def launch_task(
    connection: psycopg2._psycopg.connection,
    queue: str,
    name: str,
    lock: str,
    kwargs: types.JSONDict,
) -> int:
    with connection.cursor() as cursor:
        cursor.execute(
            """INSERT INTO tasks (queue_id, task_type, targeted_object, args)
               SELECT id, %s, %s, %s FROM queues WHERE queue_name=%s
               RETURNING id;""",
            (name, lock, kwargs, queue),
        )
        row = cursor.fetchone()

    if not row:
        raise exceptions.QueueNotFound(queue)

    connection.commit()
    return row[0]


def get_tasks(
    connection: psycopg2._psycopg.connection, queue: str
) -> Iterator[TaskRow]:
    with connection.cursor(cursor_factory=RealDictCursor) as cursor:
        while True:
            cursor.execute(
                """SELECT id, args, targeted_object, task_type FROM fetch_task(%s);""",
                (queue,),
            )
            connection.commit()

            row = cursor.fetchone()

            # fetch_tasks will always return a row, but is there's no relevant
            # value, it will all be None
            if row["id"] is None:
                return

            yield TaskRow(**row)


def finish_task(
    connection: psycopg2._psycopg.connection, task_id: int, status: str
) -> None:
    with connection.cursor() as cursor:
        cursor.execute("""SELECT finish_task(%s, %s);""", (task_id, status))

    connection.commit()


def register_queue(
    connection: psycopg2._psycopg.connection, queue: str
) -> Optional[int]:
    with connection.cursor() as cursor:
        cursor.execute(
            """INSERT INTO queues (queue_name)
               VALUES (%s)
               ON CONFLICT DO NOTHING
               RETURNING id
               """,
            (queue,),
        )
        row = cursor.fetchone()

    connection.commit()

    return row[0] if row else None


def listen_queue(connection: psycopg2._psycopg.connection, queue: str) -> None:
    queue_name = sql.Identifier(f"queue#{queue}")

    with connection.cursor() as cursor:
        cursor.execute(
            sql.SQL("""LISTEN {queue_name};""").format(queue_name=queue_name)
        )


init_pg_extensions()
