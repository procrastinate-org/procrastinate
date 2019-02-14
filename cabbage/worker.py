import logging
import select

import psycopg2
from psycopg2.extras import RealDictCursor

from cabbage.tasks import TaskManager, get_global_connection

logger = logging.getLogger(__name__)


def worker(task_manager: TaskManager, queue: str):
    conn = get_global_connection()
    # import psycopg2.extensions

    # psycopg2.extensions.register_adapter(dict, psycopg2.extras.Json)

    curs = conn.cursor(cursor_factory=RealDictCursor)
    # SQL injection !
    curs.execute(f"""LISTEN "queue#{queue}";""")

    while True:
        process_tasks(task_manager, queue, curs)
        print("waiting")
        select.select([conn], [], [], 10) == ([], [], [])


def process_tasks(task_manager: TaskManager, queue: str, curs):
    while True:
        curs.execute("select * from fetch_task(%s);", (queue,))
        result = curs.fetchone()
        if result["id"] is None:
            break

        task_id = result["id"]
        state = "done"
        # TODO: state = "error"
        try:
            call_task(task_manager, result)
            state = "done"
        finally:
            curs.execute("SELECT finish_task(%s, %s);", (task_id, state))


class CabbageException(Exception):
    pass


class TaskNotFound(CabbageException):
    pass


class TaskError(CabbageException):
    pass


def call_task(task_manager: TaskManager, result: dict):
    try:
        task = task_manager.tasks[result["task_type"]]
    except KeyError:
        raise TaskNotFound(result)

    kwargs = result["kwargs"]
    logger.info(f"About to launch task {task.name} with args {kwargs}")
    try:
        task.run(**kwargs)
    except Exception:
        logger.info(f"Error launched task {task.name} with args {kwargs}")
        raise TaskError()
    else:
        logger.info(f"Succesfully launched task {task.name} with args {kwargs}")
