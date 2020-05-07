import asyncio
import contextlib
import logging
import time
from typing import Iterable, Optional, Set, Union

from procrastinate import app, exceptions, job_context, jobs, signals, tasks

logger = logging.getLogger(__name__)


DEFAULT_WORKER_NAME = "worker"


class Worker:
    def __init__(
        self,
        app: app.App,
        queues: Optional[Iterable[str]] = None,
        name: Optional[str] = None,
        wait: bool = True,
        timeout: float = app.WORKER_TIMEOUT,
    ):
        self.app = app
        self.queues = queues
        self.worker_name: str = name or DEFAULT_WORKER_NAME
        self.timeout = timeout
        self.wait = wait

        # Handling the info about the currently running task.
        self.known_missing_tasks: Set[str] = set()
        self.job_store = self.app.job_store

        if name:
            self.logger = logger.getChild(name)
        else:
            self.logger = logger

        self.base_context: job_context.JobContext = job_context.JobContext(
            app=app, worker_name=self.worker_name, worker_queues=self.queues
        )
        self.current_context: job_context.JobContext = self.base_context
        self.stop_requested = False
        self.notify_event: Optional[asyncio.Event] = None

    @contextlib.contextmanager
    def listener(self):
        assert self.notify_event
        notifier = asyncio.ensure_future(
            self.job_store.listen_for_jobs(event=self.notify_event, queues=self.queues)
        )
        try:
            yield
        finally:
            notifier.cancel()

    async def run(self) -> None:
        self.notify_event = asyncio.Event()
        self.stop_requested = False

        self.logger.info(
            f"Starting worker on {self.base_context.queues_display}",
            extra=self.base_context.log_extra(
                action="start_worker", queues=self.queues
            ),
        )

        with self.listener(), signals.on_stop(self.stop):
            await self.single_worker()

        self.logger.info(
            f"Stopped worker on {self.base_context.queues_display}",
            extra=self.base_context.log_extra(action="stop_worker", queues=self.queues),
        )
        self.notify_event = None

    async def single_worker(self):
        while not self.stop_requested:
            job = await self.job_store.fetch_job(self.queues)
            if job:
                await self.process_job(job=job)
            else:
                if not self.wait or self.stop_requested:
                    break
                await self.wait_for_job()

    async def wait_for_job(self):
        assert self.notify_event
        self.logger.debug(
            f"Waiting for new jobs on queues " f"{self.base_context.queues_display}",
            extra=self.base_context.log_extra(
                action="waiting_for_jobs", queues=self.queues
            ),
        )

        self.notify_event.clear()
        try:
            await asyncio.wait_for(self.notify_event.wait(), timeout=self.timeout)
        except TimeoutError:
            pass
        else:
            self.notify_event.clear()

    async def process_job(self, job: jobs.Job) -> None:
        self.current_context = context = self.base_context.evolve(job=job)
        self.logger.debug(
            f"Loaded job info, about to start job {job.call_string}",
            extra=context.log_extra(action="loaded_job_info"),
        )

        status = jobs.Status.FAILED
        next_attempt_scheduled_at = None
        try:
            await self.run_job(job=job, context=context)
            status = jobs.Status.SUCCEEDED
        except exceptions.JobRetry as e:
            status = jobs.Status.TODO
            next_attempt_scheduled_at = e.scheduled_at
        except exceptions.JobError:
            pass
        except exceptions.TaskNotFound as exc:
            self.logger.exception(
                f"Task was not found: {exc}",
                extra=context.log_extra(action="task_not_found", exception=str(exc)),
            )
        finally:
            await self.job_store.finish_job(
                job=job, status=status, scheduled_at=next_attempt_scheduled_at
            )

            self.logger.debug(
                f"Acknowledged job completion {job.call_string}",
                extra=context.log_extra(action="finish_task", status=status),
            )
            self.current_job_context = None

    def load_task(self, task_name: str, context: job_context.JobContext) -> tasks.Task:
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
            extra=context.log_extra(action="load_dynamic_task", task_name=task_name),
        )

        self.app.tasks[task_name] = task
        return task

    async def run_job(self, job: jobs.Job, context: job_context.JobContext) -> None:
        task_name = job.task_name

        task = self.load_task(task_name=task_name, context=context)

        self.current_context = context = context.evolve(task=task)

        start_time = context.additional_context["start_timestamp"] = time.time()

        self.logger.info(
            f"Starting job {job.call_string}",
            extra=context.log_extra(action="start_job"),
        )
        exc_info: Union[bool, Exception]
        job_args = []
        if task.pass_context:
            job_args.append(context)
        try:
            task_result = task(*job_args, **job.task_kwargs)
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
            end_time = time.time()
            duration = end_time - start_time
            context.additional_context.update(
                {
                    "end_timestamp": end_time,
                    "duration": duration,
                    "result": task_result,
                }
            )

            extra = context.log_extra(action=log_action)

            text = f"{log_title} - Job {job.call_string} " f"in {duration:.3f} s"
            self.logger.log(log_level, text, extra=extra, exc_info=exc_info)

    def stop(self):
        # Ensure worker will stop after finishing their task
        self.stop_requested = True
        # Ensure workers currently waiting are awakened
        if self.notify_event:
            self.notify_event.set()

        # Logging

        context = self.current_context
        if context.job:
            message = (
                f"Stop requested, waiting for job to finish: "
                f"{context.job.call_string}"
            )
        else:
            message = "Stop requested, no job currently running"

        self.logger.info(message, extra=context.log_extra(action="stopping_worker"))
