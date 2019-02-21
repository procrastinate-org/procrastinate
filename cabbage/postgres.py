import psycopg2

from psycopg2 import sql


def init_pg_extensions():
    psycopg2.extensions.register_adapter(dict, psycopg2.extras.Json)


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


def get_global_connection(**kwargs):
    global _connection
    if _connection is None:
        _connection = psycopg2.connect("", **kwargs)
    return _connection

def reset_global_connection():
    global _connection
    _connection = None
    
    
init_pg_extensions()
_connection = None
