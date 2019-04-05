import logging
import select

from cabbage import exceptions, postgres, signals, tasks

logger = logging.getLogger(__name__)


SOCKET_TIMEOUT = 5  # seconds


class Worker:
    def __init__(self, task_manager: tasks.TaskManager, queue: str) -> None:
        self._task_manager = task_manager
        self._queue = queue
        self._stop_requested = False

    def run(self, timeout: int = SOCKET_TIMEOUT) -> None:
        connection = self._task_manager.connection

        postgres.listen_queue(connection=connection, queue=self._queue)

        while True:
            with signals.on_stop(self.stop):
                self.process_tasks()

            if self._stop_requested:
                break

            logger.debug("Waiting")
            select.select([connection], [], [], timeout)

    def process_tasks(self) -> None:
        for task_row in self._task_manager.get_tasks(self._queue):  # pragma: no branch
            assert isinstance(task_row.id, int)
            task_id = task_row.id

            status = "error"
            try:
                logger.debug(f"""About to run task from row {task_row})""")
                self.run_task(task_row=task_row)
                status = "done"
            except exceptions.TaskError:
                pass
            finally:
                logger.debug(f"Calling finish_task({task_id}, {status})")
                self._task_manager.finish_task(task_row, status=status)

            if self._stop_requested:
                break

    def run_task(self, task_row: postgres.TaskRow) -> None:
        task_name = task_row.task_type
        try:
            task = self._task_manager.tasks[task_name]
        except KeyError:
            raise exceptions.TaskNotFound(task_row)

        pk = task_row.id

        kwargs = task_row.args

        description = f"{task.queue}.{task.name}.{pk}({kwargs})"
        logger.info(f"Start - {description}")
        try:
            task.func(**kwargs)
        except Exception as e:
            logger.exception(f"Error - {description}")
            raise exceptions.TaskError() from e
        else:
            logger.info(f"Success - {description}")

    def stop(self, signum: signals.Signals, frame: signals.FrameType) -> None:
        self._stop_requested = True
        logger.info("Stop requested, waiting for task to finish")
