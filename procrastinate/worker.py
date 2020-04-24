import asyncio
import contextlib
import logging
import time
from typing import Any, Dict, Iterable, Optional, Set, Union

import attr

from procrastinate import app, exceptions, jobs, signals, tasks, types

logger = logging.getLogger(__name__)


def queues_display(queues):
    if queues:
        return f"queues {', '.join(queues)}"
    else:
        return "all queues"


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
        self.name = name
        self.timeout = timeout
        self.wait = wait

        # Handling the info about the currently running task.
        self.known_missing_tasks: Set[str] = set()
        self.job_store = self.app.job_store

        self.worker_name: Optional[str]
        if name:
            self.logger = logger.getChild(name)
            self.worker_name = name
        else:
            self.logger = logger
            self.worker_name = None

        self.current_job_context: Optional[Dict] = None
        self.stop_requested = False
        self.notify_event = asyncio.Event()

    @contextlib.contextmanager
    def listener(self):
        notifier = asyncio.ensure_future(
            self.job_store.listen_for_jobs(event=self.notify_event, queues=self.queues)
        )
        try:
            yield
        finally:
            notifier.cancel()

    async def run(self) -> None:
        queues = self.queues
        display = queues_display(queues)

        self.logger.info(
            f"Starting worker on {display}",
            extra={
                "action": "start_worker",
                "worker_name": self.worker_name,
                "queues": queues,
            },
        )

        with self.listener(), signals.on_stop(self.stop):
            await self.single_worker()

        self.logger.info(
            f"Stopped worker on {display}",
            extra={
                "action": "stop_worker",
                "worker_name": self.worker_name,
                "queues": queues,
            },
        )

    async def single_worker(self):
        queues = self.queues
        display = queues_display(queues)

        while not self.stop_requested:
            job = await self.job_store.fetch_job(self.queues)
            if not job:
                if not self.wait:
                    break
                self.logger.debug(
                    f"Waiting for new jobs on queues {display}",
                    extra={
                        "action": "waiting_for_jobs",
                        "worker_name": self.worker_name,
                        "queues": queues,
                    },
                )
                self.notify_event.clear()
                await asyncio.wait([self.notify_event.wait()], timeout=self.timeout)
                self.notify_event.clear()
                continue
            await self.process_job(job=job)

    async def process_job(self, job: jobs.Job) -> None:
        job_context = job.get_context()
        self.current_job_context = job_context
        log_context: types.JSONDict = {
            "job": job_context,
        }
        if self.worker_name:
            log_context["worker_name"] = self.worker_name

        self.logger.debug(
            f"Loaded job info, about to start job {job_context['call_string']}",
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
                f"Acknowledged job completion {job_context['call_string']}",
                extra={"action": "finish_task", "status": status, **log_context},
            )
            self.current_job_context = None

    def load_task(self, task_name: str, log_context: types.JSONDict) -> tasks.Task:
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
            extra={
                "action": "load_dynamic_task",
                "task_name": task_name,
                **log_context,
            },
        )

        self.app.tasks[task_name] = task
        return task

    async def run_job(self, job: jobs.Job, log_context: types.JSONDict) -> None:
        task_name = job.task_name

        assert isinstance(log_context["job"], dict)
        job_context = log_context["job"]

        task = self.load_task(task_name=task_name, log_context=log_context)

        start_time = time.time()
        job_context["start_timestamp"] = time.time()

        self.logger.info(
            f"Starting job {job_context['call_string']}",
            extra={"action": "start_job", **log_context},
        )
        exc_info: Union[bool, Exception]
        job_args = ()
        if task.pass_context:
            context = JobContext(
                worker_name=self.name, worker_queues=self.queues, job=job, task=task,
            )
            job_args = (context,)
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
            end_time = job_context["end_timestamp"] = time.time()
            job_context["duration_seconds"] = end_time - start_time
            extra = {"action": log_action, **log_context, "result": task_result}

            text = (
                f"{log_title} - Job {job_context['call_string']} "
                f"in {job_context['duration_seconds']:.3f} s"
            )
            self.logger.log(log_level, text, extra=extra, exc_info=exc_info)

    def stop(self):
        # Ensure worker will stop after finishing their task
        self.stop_requested = True
        # Ensure workers currently waiting are awakened
        self.notify_event.set()

        # Logging
        extra: Dict[str, Any] = {
            "action": "stopping_worker",
            "worker_name": self.worker_name,
        }
        if self.current_job_context:
            message = (
                f"Stop requested, waiting for job to finish: "
                f"{self.current_job_context['call_string']}"
            )
            extra["job"] = self.current_job_context

        else:
            message = "Stop requested, no job to finish"

        self.logger.info(message, extra=extra)


@attr.dataclass(frozen=True, kw_only=True)
class JobContext:
    """Contains the context execution of a running task."""

    worker_name: Optional[str]
    worker_queues: Optional[Iterable[str]] = None
    job: jobs.Job
    task: tasks.Task
