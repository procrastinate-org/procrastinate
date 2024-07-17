from __future__ import annotations

import asyncio
import functools
import inspect
import logging
import time
from datetime import datetime
from typing import Awaitable, Callable

from procrastinate import utils
from procrastinate.exceptions import JobAborted, TaskNotFound
from procrastinate.job_context import JobContext
from procrastinate.jobs import DeleteJobCondition, Job, Status
from procrastinate.manager import JobManager
from procrastinate.tasks import Task


def _find_task(task_registry: dict[str, Task], task_name: str) -> Task:
    try:
        return task_registry[task_name]
    except KeyError as exc:
        raise TaskNotFound from exc


class JobProcessor:
    def __init__(
        self,
        *,
        task_registry: dict[str, Task],
        job_manager: JobManager,
        job_queue: asyncio.Queue[Job],
        job_semaphore: asyncio.Semaphore,
        fetch_job_condition: asyncio.Condition,
        worker_id: int,
        base_context: JobContext,
        logger: logging.Logger = logging.getLogger(__name__),
        delete_jobs: str | DeleteJobCondition = DeleteJobCondition.NEVER.value,
    ):
        self.worker_id = worker_id
        self._task_registry = task_registry
        self._job_manager = job_manager
        self._job_queue = job_queue
        self._job_semaphore = job_semaphore
        self._fetch_job_condition = fetch_job_condition
        self._delete_jobs = (
            DeleteJobCondition(delete_jobs)
            if isinstance(delete_jobs, str)
            else delete_jobs
        )
        self._base_context = base_context.evolve(
            worker_id=self.worker_id,
            additional_context=base_context.additional_context.copy(),
        )

        self.logger = logger
        self.job_context: JobContext | None = None
        self._retry_at: datetime | None = None

    def _create_job_context(self, job: Job) -> JobContext:
        task = _find_task(self._task_registry, job.task_name)
        return self._base_context.evolve(task=task, job=job)

    async def _persist_job_status(self, job: Job, status: Status):
        if self._retry_at:
            await self._job_manager.retry_job(job=job, retry_at=self._retry_at)
        else:
            delete_job = {
                DeleteJobCondition.ALWAYS: True,
                DeleteJobCondition.NEVER: False,
                DeleteJobCondition.SUCCESSFUL: status == Status.SUCCEEDED,
            }[self._delete_jobs]
            await self._job_manager.finish_job(
                job=job, status=status, delete_job=delete_job
            )

        self.job_context = None
        self._job_queue.task_done()
        self.logger.debug(
            f"Acknowledged job completion {job.call_string}",
            extra=self._base_context.log_extra(action="finish_task", status=status),
        )

    async def run(self):
        while True:
            job = await self._job_queue.get()
            async with self._job_semaphore:
                status = Status.FAILED
                try:
                    self.job_context = self._create_job_context(job)
                    self.logger.debug(
                        f"Loaded job info, about to start job {job.call_string}",
                        extra=self.job_context.log_extra(action="loaded_job_info"),
                    )
                    process_job_task = asyncio.create_task(self._process_job())

                    try:
                        # the job is shielded from cancellation to enable graceful stop
                        await asyncio.shield(process_job_task)
                    except asyncio.CancelledError:
                        await process_job_task
                        status = Status.SUCCEEDED
                        raise

                    status = Status.SUCCEEDED
                except TaskNotFound as exc:
                    self.logger.exception(
                        f"Task was not found: {exc}",
                        extra=self._base_context.log_extra(
                            action="task_not_found", exception=str(exc)
                        ),
                    )
                except JobAborted:
                    status = Status.ABORTED
                except Exception:
                    # exception is already logged by _process_job, carry on
                    pass
                finally:
                    persist_job_status_task = asyncio.create_task(
                        self._persist_job_status(job=job, status=status)
                    )
                    try:
                        # prevent cancellation from stopping persistence of job status
                        await asyncio.shield(persist_job_status_task)
                    except asyncio.CancelledError:
                        await persist_job_status_task
                        raise

                    async with self._fetch_job_condition:
                        self._fetch_job_condition.notify()

    async def _process_job(self):
        assert self.job_context
        assert self.job_context.task
        assert self.job_context.job
        assert self.job_context.job_result

        task = self.job_context.task
        job = self.job_context.job
        job_result = self.job_context.job_result

        start_time = time.time()
        job_result.start_timestamp = start_time
        self.logger.info(
            f"Starting job {self.job_context.job.call_string}",
            extra=self.job_context.log_extra(action="start_job"),
        )

        job_args = []

        if task.pass_context:
            job_args.append(self.job_context)

        task_result = None
        log_title = "Error"
        log_action = "job_error"
        log_level = logging.ERROR
        exc_info: bool | BaseException = False

        await_func: Callable[..., Awaitable]
        if inspect.iscoroutinefunction(task.func):
            await_func = task
        else:
            await_func = functools.partial(utils.sync_to_async, task)

        try:
            task_result = await await_func(*job_args, **job.task_kwargs)
            # In some cases, the task function might be a synchronous function
            # that returns an awaitable without actually being a
            # coroutinefunction. In that case, in the await above, we haven't
            # actually called the task, but merely generated the awaitable that
            # implements the task. In that case, we want to wait this awaitable.
            # It's easy enough to be in that situation that the best course of
            # action is probably to await the awaitable.
            # It's not even sure it's worth emitting a warning
            if inspect.isawaitable(task_result):
                task_result = await task_result
        except JobAborted as e:
            task_result = None
            log_title = "Aborted"
            log_action = "job_aborted"
            log_level = logging.INFO
            exc_info = e
            raise
        except BaseException as e:
            task_result = None
            log_title = "Error"
            log_action = "job_error"
            log_level = logging.ERROR
            exc_info = e

            job_retry = task.get_retry_exception(exception=e, job=job)
            if job_retry:
                self._retry_at = job_retry.scheduled_at
                log_title = "Error, to retry"
                log_action = "job_error_retry"
                log_level = logging.INFO
            else:
                self._retry_at = None
            raise
        else:
            log_title = "Success"
            log_action = "job_success"
            log_level = logging.INFO
            exc_info = False
            self._retry_at = None
        finally:
            end_time = time.time()
            duration = end_time - start_time
            job_result.end_timestamp = end_time
            job_result.result = task_result

            extra = self.job_context.log_extra(action=log_action)

            text = (
                f"Job {job.call_string} ended with status: {log_title}, "
                f"lasted {duration:.3f} s"
            )
            if task_result:
                text += f" - Result: {task_result}"[:250]
            self.logger.log(log_level, text, extra=extra, exc_info=exc_info)
