from typing import Any

import psycopg2
from psycopg2 import sql

from cabbage import types


def init_pg_extensions() -> None:
    psycopg2.extensions.register_adapter(dict, psycopg2.extras.Json)


def launch_task(queue: str, name: str, lock: str, kwargs: types.JSONValue) -> None:

    conn = get_global_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            """INSERT INTO tasks (queue_id, task_type, targeted_object, args)
               SELECT id, %s, %s, %s FROM queues WHERE queue_name=%s;""",
            (name, lock, kwargs, queue),
        )
    conn.commit()


def register_queue(queue: str) -> None:
    conn = get_global_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            """INSERT INTO queues (queue_name) VALUES (%s) ON CONFLICT DO NOTHING""",
            (queue,),
        )
    conn.commit()


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


init_pg_extensions()
_connection = None
