import asyncio
import logging
import time
from typing import Iterable, NoReturn, Optional, Set, Union

from procrastinate import app, exceptions, jobs, signals, tasks, types

logger = logging.getLogger(__name__)


class Worker:
    def __init__(
        self,
        app: app.App,
        queues: Optional[Iterable[str]] = None,
        import_paths: Optional[Iterable[str]] = None,
        name: Optional[str] = None,
    ):
        self.app = app
        self.queues = queues
        self.name = name
        self.stop_requested = False
        # Handling the info about the currently running task.
        self.log_context: types.JSONDict = {}
        self.known_missing_tasks: Set[str] = set()

        self.app.perform_import_paths()
        self.job_store = self.app.job_store

        if name:
            self.logger = logger.getChild(name)
            self.log_context["worker_name"] = name
        else:
            self.logger = logger

    async def run(self) -> None:
        queues = self.queues
        await self.job_store.listen_for_jobs(queues=queues)

        if queues:
            queue_names = f"queues {', '.join(queues)}"
        else:
            queue_names = "all queues"

        self.logger.info(
            f"Starting worker on queues {queue_names}",
            extra={"action": "start_worker", "queues": queues},
        )
        with signals.on_stop(self.stop):
            while not self.stop_requested:

                try:
                    await self.process_jobs_once()
                except exceptions.StopRequested:
                    break
                except exceptions.NoMoreJobs:
                    self.logger.debug(
                        f"Waiting for new jobs on queues {queue_names}",
                        extra={"action": "waiting_for_jobs", "queues": queues},
                    )

                await self.job_store.wait_for_jobs()

        self.logger.info(
            f"Stopped worker on {queue_names}",
            extra={"action": "stop_worker", "queues": queues},
        )

    async def process_jobs_once(self) -> NoReturn:
        while True:
            # We only leave this loop with an exception:
            # either NoMoreJobs or StopRequested
            await self.process_next_job()

    async def process_next_job(self) -> None:
        log_context = self.log_context
        job = await self.job_store.fetch_job(self.queues)
        if job is None:
            raise exceptions.NoMoreJobs

        job_context = log_context["job"] = {**job.get_context()}
        self.logger.debug(
            f"Loaded job info, about to start job {job_context['call_string']}",
            extra={"action": "loaded_job_info", **log_context},
        )

        status = jobs.Status.FAILED
        next_attempt_scheduled_at = None
        try:
            await self.run_job(job=job)
            status = jobs.Status.SUCCEEDED
        except exceptions.JobRetry as e:
            status = jobs.Status.TODO
            next_attempt_scheduled_at = e.scheduled_at
        except exceptions.JobError:
            pass
        except exceptions.TaskNotFound as exc:
            self.logger.exception(
                f"Task was not found: {exc}",
                extra={"action": "task_not_found", "exception": str(exc)},
            )
        finally:
            await self.job_store.finish_job(
                job=job, status=status, scheduled_at=next_attempt_scheduled_at
            )

            self.logger.debug(
                f"Acknowledged job completion {job_context['call_string']}",
                extra={"action": "finish_task", "status": status, **log_context},
            )

        if self.stop_requested:
            raise exceptions.StopRequested

    def load_task(self, task_name) -> tasks.Task:
        if task_name in self.known_missing_tasks:
            raise exceptions.TaskNotFound(f"Cancelling job for {task_name} (not found)")

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

    async def run_job(self, job: jobs.Job) -> None:
        log_context = self.log_context
        task_name = job.task_name

        task = self.load_task(task_name=task_name)

        # We store the log context in self. This way, when requesting
        # a stop, we can get details on the currently running task
        # in the logs.
        start_time = time.time()

        job_context = log_context["job"] = {
            **job.get_context(),
            "start_timestamp": time.time(),
        }
        exc_info: Union[Exception, bool]

        self.logger.info(
            f"Starting job {job_context['call_string']}",
            extra={"action": "start_job", **log_context},
        )

        try:
            task_result = task(**job.task_kwargs)
            if asyncio.iscoroutine(task_result):
                task_result = await task_result

        except Exception as e:
            task_result = None
            log_title = "Job error"
            log_action = "job_error"
            log_level = logging.ERROR
            exc_info = e

            retry_exception = task.get_retry_exception(exception=e, job=job)
            if retry_exception:
                log_title = "Job error, to retry"
                log_action = "job_error_retry"
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
            ftext = (
                f"{log_title} - Job {job_context['call_string']} "
                f"in {job_context['duration_seconds']:.3f} s"
            )
            self.logger.log(log_level, ftext, extra=extra, exc_info=exc_info)

    def stop(
        self,
        signum: Optional[signals.Signals] = None,
        frame: Optional[signals.FrameType] = None,
    ) -> None:
        self.stop_requested = True
        log_context = self.log_context
        self.job_store.stop()

        if log_context:
            self.logger.info(
                f"Stop requested, waiting for current job to finish",
                extra={"action": "stopping_worker", **log_context},
            )
        else:
            self.logger.info(
                "Stop requested, no job to finish ", extra={"action": "stopping_worker"}
            )
