import logging
import select

from psycopg2.extras import RealDictCursor

from cabbage import exceptions, postgres, tasks

logger = logging.getLogger(__name__)


SOCKET_TIMEOUT = 5  # seconds


def worker(task_manager: tasks.TaskManager, queue: str):
    conn = postgres.get_global_connection()

    with conn.cursor(cursor_factory=RealDictCursor) as curs:
        postgres.listen_queue(curs, queue)

        while True:
            process_tasks(task_manager, queue, curs)
            logger.debug("waiting")
            select.select([conn], [], [], SOCKET_TIMEOUT)


def process_tasks(task_manager: tasks.TaskManager, queue: str, curs):
    while True:
        curs.execute("""SELECT * FROM fetch_task(%s);""", (queue,))
        curs.connection.commit()

        result = curs.fetchone()
        if result["id"] is None:
            break

        task_id = result["id"]

        state = "error"
        try:
            logger.debug(f"""About to run task from row {result})""")
            call_task(task_manager, result)
            state = "done"
        except exceptions.TaskError:
            pass
        finally:
            curs.execute("""SELECT finish_task(%s, %s);""", (task_id, state))
            logger.debug(f"Commiting finish_task({task_id}, {state})")
            curs.connection.commit()


def call_task(task_manager: tasks.TaskManager, result: dict):
    try:
        task = task_manager.tasks[result["task_type"]]
    except KeyError:
        raise exceptions.TaskNotFound(result)

    task_run = tasks.TaskRun(task=task, id=result["id"], lock=result["targeted_object"])
    kwargs = result["args"]
    logger.info(f"About to launch task {task.name} with args {kwargs}")
    try:
        task_run.run(**kwargs)
    except Exception as e:
        logger.exception(f"Error run task {task.name} with args {kwargs}")
        raise exceptions.TaskError() from e
    else:
        logger.info(f"Succesfully ran task {task.name} with args {kwargs}")
