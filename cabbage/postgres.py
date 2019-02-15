import functools
import psycopg2

from psycopg2 import sql


def launch_task(queue, name, lock, kwargs):

    conn = get_global_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            """INSERT INTO tasks (queue_id, task_type, targeted_object, args)
               SELECT id, %s, %s, %s FROM queues WHERE queue_name=%s;""",
            (name, lock, kwargs, queue),
        )
    conn.commit()


def register_queue(queue):
    conn = get_global_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            """INSERT INTO queues (queue_name) VALUES (%s) ON CONFLICT DO NOTHING""",
            (queue,),
        )
    conn.commit()


def listen_queue(curs, queue):
    queue_name = sql.Identifier(f"queue#{queue}")
    curs.execute(sql.SQL("""LISTEN {queue_name};""").format(queue_name=queue_name))


@functools.lru_cache(1)
def get_global_connection():
    conn = psycopg2.connect("")
    # conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    psycopg2.extensions.register_adapter(dict, psycopg2.extras.Json)
    return conn
