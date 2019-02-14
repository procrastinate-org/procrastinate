import logging
import select

from psycopg2.extras import RealDictCursor

from cabbage import tasks

logger = logging.getLogger(__name__)


SOCKET_TIMEOUT = 10  # seconds


def worker(task_manager: tasks.TaskManager, queue: str):
    conn = tasks.get_global_connection()

    with conn.cursor(cursor_factory=RealDictCursor) as curs:
        # SQL injection !
        curs.execute(f"""LISTEN "queue#{queue}";""")

        while True:
            process_tasks(task_manager, queue, curs)
            logger.debug("waiting")
            select.select([conn], [], [], SOCKET_TIMEOUT) == ([], [], [])


def process_tasks(task_manager: tasks.TaskManager, queue: str, curs):
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


def call_task(task_manager: tasks.TaskManager, result: dict):
    try:
        task = task_manager.tasks[result["task_type"]]
    except KeyError:
        raise TaskNotFound(result)

    task_run = tasks.TaskRun(task=task, id=result["id"], lock=result["targeted_object"])
    kwargs = result["args"]
    logger.info(f"About to launch task {task.name} with args {kwargs}")
    try:
        task_run.run(**kwargs)
    except Exception:
        logger.info(f"Error launched task {task.name} with args {kwargs}")
        raise TaskError()
    else:
        logger.info(f"Succesfully launched task {task.name} with args {kwargs}")
