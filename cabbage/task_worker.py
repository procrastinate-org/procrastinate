import functools
import logging
import select
from typing import Any, Callable

from cabbage import exceptions, postgres, tasks

logger = logging.getLogger(__name__)


SOCKET_TIMEOUT = 5  # seconds


def worker(
    task_manager: tasks.TaskManager, queue: str, timeout: int = SOCKET_TIMEOUT
) -> None:
    conn = postgres.get_global_connection()

    with postgres.get_dict_cursor(conn) as curs:
        postgres.listen_queue(curs, queue)
        infinite_loop(
            functools.partial(
                one_loop,
                task_manager=task_manager,
                queue=queue,
                curs=curs,
                timeout=timeout,
            )
        )


def infinite_loop(func: Callable) -> None:
    while True:
        func()


def one_loop(task_manager: tasks.TaskManager, queue: str, curs: Any, timeout) -> None:
    process_tasks(task_manager=task_manager, queue=queue, curs=curs)
    logger.debug("waiting")
    select.select([curs.connection], [], [], timeout)


def process_tasks(task_manager: tasks.TaskManager, queue: str, curs: Any) -> None:

    for task_row in postgres.get_tasks(cursor=curs, queue=queue):  # pragma: no branch

        assert isinstance(task_row.id, int)
        task_id = task_row.id

        status = "error"
        try:
            logger.debug(f"""About to run task from row {task_row})""")
            call_task(task_manager=task_manager, task_row=task_row)
            status = "done"
        except exceptions.TaskError:
            pass
        finally:
            logger.debug(f"Calling finish_task({task_id}, {status})")
            postgres.finish_task(cursor=curs, task_id=task_id, status=status)


def call_task(task_manager: tasks.TaskManager, task_row: postgres.TaskRow) -> None:
    task_name = task_row.task_type
    try:
        task = task_manager.tasks[task_name]
    except KeyError:
        raise exceptions.TaskNotFound(task_row)

    pk = task_row.id

    task_run = tasks.TaskRun(task=task, id=pk, lock=task_row.targeted_object)
    kwargs = task_row.args

    description = f"{task.queue}.{task.name}.{pk}({kwargs})"
    logger.info(f"Start - {description}")
    try:
        task_run.run(**kwargs)
    except Exception as e:
        logger.exception(f"Error - {description}")
        raise exceptions.TaskError() from e
    else:
        logger.info(f"Succesfully ran task {task.name} with args {kwargs}")
