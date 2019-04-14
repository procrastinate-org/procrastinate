import logging
import select
import time

from cabbage import exceptions, postgres, signals, tasks, types

logger = logging.getLogger(__name__)


SOCKET_TIMEOUT = 5  # seconds


class Worker:
    def __init__(self, task_manager: tasks.TaskManager, queue: str) -> None:
        self._task_manager = task_manager
        self._queue = queue
        self._stop_requested = False
        # Handling the info about the currently running task.
        self.log_context: types.JSONDict = {}

    def run(self, timeout: int = SOCKET_TIMEOUT) -> None:
        connection = self._task_manager.connection

        postgres.listen_queue(connection=connection, queue=self._queue)

        while True:
            with signals.on_stop(self.stop):
                self.process_tasks()

            if self._stop_requested:
                logger.debug(
                    "Finished running task at the end of the batch",
                    extra={"action": "stopped_end_batch"},
                )
                break

            logger.debug("Waiting for new tasks", extra={"action": "waiting_for_tasks"})
            select.select([connection], [], [], timeout)

    def process_tasks(self) -> None:
        for task_row in self._task_manager.get_tasks(self._queue):  # pragma: no branch
            assert isinstance(task_row.id, int)
            log_context = {"row": task_row._asdict(), "queue": self._queue}
            logger.debug(
                "Loaded task row, about to start task",
                extra={"action": "loaded_task_row", **log_context},
            )

            status = "error"
            try:
                self.run_task(task_row=task_row)
                status = "done"
            except exceptions.TaskError:
                pass
            finally:
                self._task_manager.finish_task(task_row, status=status)
                logger.debug(
                    "Acknowledged task row completion",
                    extra={"action": "finish_task", "status": status, **log_context},
                )

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

        # We store the log context in self. This way, when requesting
        # a stop, we can get details on the currently running task
        # in the logs.
        start_time = time.time()
        log_context = self.log_context = {
            "queue": task.queue,
            "name": task.name,
            "id": pk,
            "kwargs": kwargs,
            "start_time": time.time(),
        }
        logger.info(
            "Starting task", extra={"action": "task_start", "task": log_context}
        )
        try:
            task.func(**kwargs)
        except Exception as e:
            end_time = log_context["end_time"] = time.time()
            log_context["duration"] = end_time - start_time

            logger.exception(
                "Task error", extra={"action": "task_error", "task": log_context}
            )
            raise exceptions.TaskError() from e
        else:
            end_time = log_context["end_time"] = time.time()
            log_context["duration"] = end_time - start_time
            logger.info(
                "Task success", extra={"action": "task_success", "task": log_context}
            )

    def stop(self, signum: signals.Signals, frame: signals.FrameType) -> None:
        self._stop_requested = True
        log_context = self.log_context

        logger.info(
            "Stop requested, waiting for current task to finish",
            extra={"action": "stopping_worker", "task": log_context},
        )
