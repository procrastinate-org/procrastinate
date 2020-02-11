import asyncio
import logging
import time
from typing import Iterable, Optional, Set

from procrastinate import app, exceptions, jobs, signals, tasks, types

logger = logging.getLogger(__name__)

WORKER_TIMEOUT = 5.0  # seconds


class Worker:
    def __init__(
        self,
        app: app.App,
        queues: Optional[Iterable[str]] = None,
        import_paths: Optional[Iterable[str]] = None,
        name: Optional[str] = None,
        worker_count: int = 1,
        timeout: float = WORKER_TIMEOUT,
    ):
        self.app = app
        self.queues = queues
        self.name = name
        self.worker_count = worker_count
        self.timeout = timeout

        # Handling the info about the currently running task.
        self.known_missing_tasks: Set[str] = set()

        self.app.perform_import_paths()
        self.job_store = self.app.job_store

        self.stop_requested = False

        self.worker_name: Optional[str]
        if name:
            self.logger = logger.getChild(name)
            self.worker_name = name
        else:
            self.logger = logger
            self.worker_name = None

    async def run(self) -> None:
        notify_event = asyncio.Event()
        notifier = asyncio.create_task(
            self.job_store.listen_for_jobs(event=notify_event, queues=self.queues)
        )

        def stop(
            signum: Optional[signals.Signals] = None,
            frame: Optional[signals.FrameType] = None,
        ) -> None:
            # Ensure worker will stop after finishing their task
            self.stop_requested = True
            # Ensure workers currently waiting are awakened
            # TODO asyncio events are not thread safe. Does it mean it's dangerous to
            # call them in a signal handler too ? (I don't think so but not sure)
            notify_event.set()
            # Stop the listen/notify task
            notifier.cancel()
            # TODO log?

        with signals.on_stop(stop):
            await asyncio.gather(
                *(
                    self.single_worker(notify_event=notify_event)
                    for _ in range(self.worker_count)
                ),
            )

        self.logger.debug("Stopped worker", extra={"action": "stopped_worker"})

    async def single_worker(self, notify_event: asyncio.Event):

        while not self.stop_requested:
            job = await self.job_store.fetch_job(self.queues)
            if not job:
                self.logger.debug(
                    "Waiting for new jobs", extra={"action": "waiting_for_jobs"}
                )
                notify_event.clear()
                await asyncio.wait([notify_event.wait()], timeout=self.timeout)
                notify_event.clear()
                continue
            await self.process_job(job=job)

    async def process_job(self, job: jobs.Job) -> None:
        log_context: types.JSONDict = {
            "worker_name": self.worker_name,
            "job": job.get_context(),
        }

        self.logger.debug(
            "Loaded job info, about to start job",
            extra={"action": "loaded_job_info", **log_context},
        )

        status = jobs.Status.FAILED
        next_attempt_scheduled_at = None
        try:
            await self.run_job(job=job, log_context=log_context)
            status = jobs.Status.SUCCEEDED
        except exceptions.JobRetry as e:
            status = jobs.Status.TODO
            next_attempt_scheduled_at = e.scheduled_at
        except exceptions.JobError:
            pass
        except exceptions.TaskNotFound as exc:
            self.logger.exception(
                f"Task was not found: {exc}",
                extra={
                    "action": "task_not_found",
                    "exception": str(exc),
                    **log_context,
                },
            )
        finally:
            await self.job_store.finish_job(
                job=job, status=status, scheduled_at=next_attempt_scheduled_at
            )
            self.logger.debug(
                "Acknowledged job completion",
                extra={"action": "finish_task", "status": status, **log_context},
            )

    def load_task(self, task_name: str, log_context: types.JSONDict) -> tasks.Task:
        if task_name in self.known_missing_tasks:
            raise exceptions.TaskNotFound(
                f"Cannot run job for task {task_name} previsouly not found"
            )

        try:
            # Simple case: the task is already known
            return self.app.tasks[task_name]
        except KeyError:
            pass

        # Will raise if not found or not a task
        try:
            task = tasks.load_task(task_name)
        except exceptions.ProcrastinateException:
            self.known_missing_tasks.add(task_name)
            raise

        self.logger.warning(
            f"Task at {task_name} was not registered, it's been loaded dynamically.",
            extra={"action": "load_dynamic_task", "task_name": task_name},
        )

        self.app.tasks[task_name] = task
        return task

    async def run_job(self, job: jobs.Job, log_context: types.JSONDict) -> None:
        task_name = job.task_name

        task = self.load_task(task_name=task_name, log_context=log_context)

        log_context.setdefault("job", {})
        assert isinstance(log_context["job"], dict)
        job_context = log_context["job"]

        start_time = time.time()
        job_context["start_timestamp"] = time.time()

        self.logger.info("Starting job", extra={"action": "start_job", **log_context})
        try:
            task_result = task(**job.task_kwargs)
            if asyncio.iscoroutine(task_result):
                task_result = await task_result

        except Exception as e:
            task_result = None
            log_title = "Job error"
            log_action = "job_error"
            log_level = logging.ERROR
            exc_info = True

            retry_exception = task.get_retry_exception(job)
            if retry_exception:
                raise retry_exception from e
            raise exceptions.JobError() from e

        else:
            log_title = "Job success"
            log_action = "job_success"
            log_level = logging.INFO
            exc_info = False
        finally:
            end_time = job_context["end_timestamp"] = time.time()
            job_context["duration_seconds"] = end_time - start_time
            extra = {"action": log_action, **log_context, "result": task_result}
            self.logger.log(log_level, log_title, extra=extra, exc_info=exc_info)
