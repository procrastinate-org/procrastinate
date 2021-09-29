import asyncio
import logging
import time
from enum import Enum
from typing import Any, Dict, Iterable, Optional, Union

from procrastinate import app, exceptions, job_context, jobs, signals, tasks, utils

logger = logging.getLogger(__name__)


WORKER_NAME = "worker"
WORKER_TIMEOUT = 5.0  # seconds
WORKER_CONCURRENCY = 1  # parallel task(s)


class DeleteJobCondition(Enum):
    """
    An enumeration with all the possible conditions to delete a job
    """

    NEVER = "never"  #: Keep jobs in database after completion
    SUCCESSFUL = "successful"  #: Delete only successful jobs
    ALWAYS = "always"  #: Always delete jobs at completion


class Worker:
    def __init__(
        self,
        app: "app.App",
        queues: Optional[Iterable[str]] = None,
        name: Optional[str] = None,
        concurrency: int = WORKER_CONCURRENCY,
        wait: bool = True,
        timeout: float = WORKER_TIMEOUT,
        listen_notify: bool = True,
        delete_jobs: str = DeleteJobCondition.NEVER.value,
        additional_context: Optional[Dict[str, Any]] = None,
    ):
        self.app = app
        self.queues = queues
        self.worker_name: str = name or WORKER_NAME
        self.concurrency = concurrency

        self.timeout = timeout
        self.wait = wait
        self.listen_notify = listen_notify
        self.delete_jobs = DeleteJobCondition(delete_jobs)

        self.job_manager = self.app.job_manager

        if name:
            self.logger = logger.getChild(name)
        else:
            self.logger = logger

        # Handling the info about the currently running task.
        self.base_context: job_context.JobContext = job_context.JobContext(
            app=app,
            worker_name=self.worker_name,
            worker_queues=self.queues,
            additional_context=additional_context.copy() if additional_context else {},
        )
        self.current_contexts: Dict[int, job_context.JobContext] = {}
        self.stop_requested = False
        self.notify_event: Optional[asyncio.Event] = None

    def context_for_worker(
        self, worker_id: int, reset=False, **kwargs
    ) -> job_context.JobContext:
        """
        Retrieves the context for sub-sworker ``worker_id``. If not found, or ``reset``
        is True, context is recreated from ``self.base_context``. Additionnal parameters
        are used to update the context. The resulting context is kept and will be
        returned for later calls.
        """
        if reset or worker_id not in self.current_contexts:
            context = self.base_context
            kwargs["worker_id"] = worker_id
            kwargs["additional_context"] = self.base_context.additional_context.copy()
        else:
            context = self.current_contexts[worker_id]

        if kwargs:
            context = context.evolve(**kwargs)
            self.current_contexts[worker_id] = context

        return context

    async def listener(self):
        assert self.notify_event
        return await self.job_manager.listen_for_jobs(
            event=self.notify_event,
            queues=self.queues,
        )

    async def periodic_deferrer(self):
        return await self.app.periodic_deferrer.worker()

    async def run(self) -> None:
        self.notify_event = asyncio.Event()
        self.stop_requested = False

        self.logger.info(
            f"Starting worker on {self.base_context.queues_display}",
            extra=self.base_context.log_extra(
                action="start_worker", queues=self.queues
            ),
        )

        with signals.on_stop(self.stop):
            side_coros = [self.periodic_deferrer()]
            if self.wait and self.listen_notify:
                side_coros.append(self.listener())

            await utils.run_tasks(
                main_coros=(
                    self.single_worker(worker_id=worker_id)
                    for worker_id in range(self.concurrency)
                ),
                side_coros=side_coros,
                graceful_stop_callback=self.stop,
            )

        self.logger.info(
            f"Stopped worker on {self.base_context.queues_display}",
            extra=self.base_context.log_extra(action="stop_worker", queues=self.queues),
        )
        self.notify_event = None

    async def single_worker(self, worker_id: int):
        current_timeout = self.timeout * (worker_id + 1)
        while not self.stop_requested:
            job = await self.job_manager.fetch_job(self.queues)
            if job:
                await self.process_job(job=job, worker_id=worker_id)
            else:
                if not self.wait or self.stop_requested:
                    break
                await self.wait_for_job(timeout=current_timeout)
                current_timeout = self.timeout * self.concurrency

    async def wait_for_job(self, timeout: float):
        assert self.notify_event
        self.logger.debug(
            f"Waiting for new jobs on {self.base_context.queues_display}",
            extra=self.base_context.log_extra(
                action="waiting_for_jobs", queues=self.queues
            ),
        )
        self.notify_event.clear()
        try:
            await asyncio.wait_for(self.notify_event.wait(), timeout=timeout)
        except asyncio.TimeoutError:
            pass
        else:
            self.notify_event.clear()

    async def process_job(self, job: jobs.Job, worker_id: int = 0) -> None:
        context = self.context_for_worker(worker_id=worker_id, job=job)

        self.logger.debug(
            f"Loaded job info, about to start job {job.call_string}",
            extra=context.log_extra(action="loaded_job_info"),
        )

        status, retry_at = None, None
        try:
            await self.run_job(job=job, worker_id=worker_id)
            status = jobs.Status.SUCCEEDED
        except exceptions.JobRetry as e:
            retry_at = e.scheduled_at
        except exceptions.JobError:
            status = jobs.Status.FAILED
        except exceptions.TaskNotFound as exc:
            status = jobs.Status.FAILED
            self.logger.exception(
                f"Task was not found: {exc}",
                extra=context.log_extra(action="task_not_found", exception=str(exc)),
            )
        finally:
            if retry_at:
                await self.job_manager.retry_job(job=job, retry_at=retry_at)
            else:
                assert status is not None

                delete_job = {
                    DeleteJobCondition.ALWAYS: True,
                    DeleteJobCondition.NEVER: False,
                    DeleteJobCondition.SUCCESSFUL: status == jobs.Status.SUCCEEDED,
                }[self.delete_jobs]

                await self.job_manager.finish_job(
                    job=job, status=status, delete_job=delete_job
                )

            self.logger.debug(
                f"Acknowledged job completion {job.call_string}",
                extra=context.log_extra(action="finish_task", status=status),
            )
            # Remove job information from the current context
            self.context_for_worker(worker_id=worker_id, reset=True)

    def find_task(self, task_name: str) -> tasks.Task:
        try:
            return self.app.tasks[task_name]
        except KeyError:
            raise exceptions.TaskNotFound

    async def run_job(self, job: jobs.Job, worker_id: int) -> None:
        task_name = job.task_name

        task = self.find_task(task_name=task_name)

        context = self.context_for_worker(worker_id=worker_id, task=task)

        start_time = time.time()
        context.job_result.start_timestamp = start_time

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
            elif self.concurrency != 1:
                logger.warning(
                    "When using worker concurrency, non-async tasks will block "
                    "the whole worker.",
                    extra=context.log_extra(action="concurrent_sync_task"),
                )

        except Exception as e:
            task_result = None
            log_title = "Error"
            log_action = "job_error"
            log_level = logging.ERROR
            exc_info = e

            retry_exception = task.get_retry_exception(exception=e, job=job)
            if retry_exception:
                log_title = "Error, to retry"
                log_action = "job_error_retry"
                raise retry_exception from e
            raise exceptions.JobError() from e

        else:
            log_title = "Success"
            log_action = "job_success"
            log_level = logging.INFO
            exc_info = False
        finally:
            end_time = time.time()
            duration = end_time - start_time
            context.job_result.end_timestamp = end_time
            context.job_result.result = task_result

            extra = context.log_extra(action=log_action)

            text = (
                f"Job {job.call_string} ended with status: {log_title}, "
                f"lasted {duration:.3f} s"
            )
            if task_result:
                text += f" - Result: {task_result}"[:250]
            self.logger.log(log_level, text, extra=extra, exc_info=exc_info)

    def stop(self):
        # Ensure worker will stop after finishing their task
        self.stop_requested = True
        # Ensure workers currently waiting are awakened
        if self.notify_event:
            self.notify_event.set()

        # Logging

        self.logger.info(
            "Stop requested",
            extra=self.base_context.log_extra(action="stopping_worker"),
        )

        contexts = [
            context for context in self.current_contexts.values() if context.job
        ]
        now = time.time()
        for context in contexts:
            self.logger.info(
                "Waiting for job to finish: "
                + context.job_description(current_timestamp=now),
                extra=context.log_extra(action="ending_job"),
            )
