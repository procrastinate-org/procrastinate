import logging
import time

from cabbage import exceptions, jobs, signals, store, tasks, types

logger = logging.getLogger(__name__)


SOCKET_TIMEOUT = 5  # seconds


class Worker:
    def __init__(self, task_manager: tasks.TaskManager, queue: str) -> None:
        self._task_manager = task_manager
        self._queue = queue
        self._stop_requested = False
        # Handling the info about the currently running task.
        self.log_context: types.JSONDict = {}

    @property
    def _job_store(self) -> store.JobStore:
        return self._task_manager.job_store

    def run(self, timeout: int = SOCKET_TIMEOUT) -> None:

        self._job_store.listen_for_jobs(queue=self._queue)

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
            self._job_store.wait_for_jobs(timeout=timeout)

    def process_tasks(self) -> None:
        for job in self._job_store.get_tasks(self._queue):  # pragma: no branch
            assert isinstance(job.id, int)

            log_context = {"row": job._asdict(), "queue": self._queue}
            logger.debug(
                "Loaded task row, about to start task",
                extra={"action": "loaded_task_row", **log_context},
            )

            status = jobs.Status.ERROR
            try:
                self.run_task(job=job)
                status = jobs.Status.DONE
            except exceptions.TaskError:
                pass
            finally:
                self._job_store.finish_task(job=job, status=status)
                logger.debug(
                    "Acknowledged task row completion",
                    extra={"action": "finish_task", "status": status, **log_context},
                )

            if self._stop_requested:
                break

    def run_task(self, job: jobs.Job) -> None:
        task_name = job.task_name
        try:
            task = self._task_manager.tasks[task_name]
        except KeyError:
            raise exceptions.TaskNotFound(job)

        pk = job.id

        kwargs = job.kwargs

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
            task(**kwargs)
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
