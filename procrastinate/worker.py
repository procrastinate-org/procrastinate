from __future__ import annotations

import asyncio
import contextlib
import functools
import inspect
import logging
import time
from typing import Any, Awaitable, Callable, Iterable

from procrastinate import signals, utils
from procrastinate.app import App
from procrastinate.exceptions import JobAborted, JobRetry, TaskNotFound
from procrastinate.job_context import JobContext
from procrastinate.jobs import DeleteJobCondition, Job, Status
from procrastinate.periodic import PeriodicDeferrer
from procrastinate.retry import RetryDecision
from procrastinate.tasks import Task

logger = logging.getLogger(__name__)

WORKER_NAME = "worker"
WORKER_CONCURRENCY = 1  # maximum number of parallel jobs
POLLING_INTERVAL = 5.0  # seconds


class Worker:
    def __init__(
        self,
        app: App,
        queues: Iterable[str] | None = None,
        name: str | None = WORKER_NAME,
        concurrency: int = WORKER_CONCURRENCY,
        wait: bool = True,
        timeout: float = POLLING_INTERVAL,
        listen_notify: bool = True,
        delete_jobs: str | DeleteJobCondition = DeleteJobCondition.NEVER.value,
        additional_context: dict[str, Any] | None = None,
        install_signal_handlers: bool = True,
    ):
        self.app = app
        self.queues = queues
        self.worker_name = name
        self.concurrency = concurrency
        self.wait = wait
        self.polling_interval = timeout
        self.listen_notify = listen_notify
        self.delete_jobs = (
            DeleteJobCondition(delete_jobs)
            if isinstance(delete_jobs, str)
            else delete_jobs
        )
        self.additional_context = additional_context
        self.install_signal_handlers = install_signal_handlers

        if self.worker_name:
            self.logger = logger.getChild(self.worker_name)
        else:
            self.logger = logger

        self.base_context = JobContext(
            app=app,
            worker_name=self.worker_name,
            worker_queues=self.queues,
            additional_context=additional_context.copy() if additional_context else {},
        )

        self._run_task: asyncio.Task | None = None

    def stop(self):
        self.logger.info(
            "Stop requested",
            extra=self.base_context.log_extra(action="stopping_worker"),
        )

        if self._run_task:
            self._run_task.cancel()

    async def periodic_deferrer(self):
        deferrer = PeriodicDeferrer(
            registry=self.app.periodic_registry,
            **self.app.periodic_defaults,
        )
        return await deferrer.worker()

    def find_task(self, task_name: str) -> Task:
        try:
            return self.app.tasks[task_name]
        except KeyError as exc:
            raise TaskNotFound from exc

    async def _persist_job_status(
        self, job: Job, status: Status, retry_decision: RetryDecision | None
    ):
        if retry_decision:
            await self.app.job_manager.retry_job(
                job=job,
                retry_at=retry_decision.retry_at,
                lock=retry_decision.lock,
                priority=retry_decision.priority,
                queue=retry_decision.queue,
            )
        else:
            delete_job = {
                DeleteJobCondition.ALWAYS: True,
                DeleteJobCondition.NEVER: False,
                DeleteJobCondition.SUCCESSFUL: status == Status.SUCCEEDED,
            }[self.delete_jobs]
            await self.app.job_manager.finish_job(
                job=job, status=status, delete_job=delete_job
            )

    @staticmethod
    def _log_job_outcome(
        status: Status,
        job_context: JobContext,
        job_retry: JobRetry | None,
        exc_info: bool | BaseException = False,
    ):
        assert job_context.job
        assert job_context.job_result
        assert job_context.job_result.start_timestamp
        assert job_context.job_result.end_timestamp

        if status == Status.SUCCEEDED:
            log_action, log_title = "job_success", "Success"
        elif status == Status.ABORTED:
            log_action, log_title = "job_aborted", "Aborted"
        elif job_retry:
            log_action, log_title = "job_error_retry", "Error, to retry"
        else:
            log_action, log_title = "job_error", "Error"

        duration = (
            job_context.job_result.end_timestamp
            - job_context.job_result.start_timestamp
        )
        text = (
            f"Job {job_context.job.call_string} ended with status: {log_title}, "
            f"lasted {duration:.3f} s"
        )
        if job_context.job_result.result:
            text += f" - Result: {job_context.job_result.result}"[:250]

        extra = job_context.log_extra(action=log_action)
        log_level = logging.ERROR if status == Status.FAILED else logging.INFO
        logger.log(log_level, text, extra=extra, exc_info=exc_info)

    async def _process_job(self, job_context: JobContext):
        """
        Processes a given job and persists its status
        """
        task = job_context.task
        job_retry = None
        exc_info = False
        retry_decision = None
        job = job_context.job
        assert job

        job_result = job_context.job_result
        job_result.start_timestamp = time.time()

        try:
            if not task:
                raise TaskNotFound

            self.logger.debug(
                f"Loaded job info, about to start job {job.call_string}",
                extra=job_context.log_extra(action="loaded_job_info"),
            )

            self.logger.info(
                f"Starting job {job.call_string}",
                extra=job_context.log_extra(action="start_job"),
            )

            exc_info: bool | BaseException = False

            await_func: Callable[..., Awaitable]
            if inspect.iscoroutinefunction(task.func):
                await_func = task
            else:
                await_func = functools.partial(utils.sync_to_async, task)

            job_args = [job_context] if task.pass_context else []
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
            job_result.result = task_result

        except BaseException as e:
            exc_info = e
            if not isinstance(e, JobAborted):
                job_retry = (
                    task.get_retry_exception(exception=e, job=job) if task else None
                )
                retry_decision = job_retry.retry_decision if job_retry else None
                if isinstance(e, TaskNotFound):
                    self.logger.exception(
                        f"Task was not found: {e}",
                        extra=self.base_context.log_extra(
                            action="task_not_found", exception=str(e)
                        ),
                    )
            if not isinstance(e, Exception):
                raise

        finally:
            job_result.end_timestamp = time.time()

            if isinstance(exc_info, JobAborted):
                status = Status.ABORTED
            elif exc_info:
                status = Status.FAILED
            else:
                status = Status.SUCCEEDED

            Worker._log_job_outcome(
                status=status,
                job_context=job_context,
                job_retry=job_retry,
                exc_info=exc_info,
            )
            await self._persist_job_status(
                job=job, status=status, retry_decision=retry_decision
            )

            self.logger.debug(
                f"Acknowledged job completion {job.call_string}",
                extra=self.base_context.log_extra(action="finish_task", status=status),
            )

    async def run(self):
        self._run_task = asyncio.current_task()
        notify_event = asyncio.Event()

        self.logger.info(
            f"Starting worker on {self.base_context.queues_display}",
            extra=self.base_context.log_extra(
                action="start_worker", queues=self.queues
            ),
        )

        job_semaphore = asyncio.Semaphore(self.concurrency)

        running_jobs: dict[JobContext, asyncio.Task] = {}
        side_tasks = [asyncio.create_task(self.periodic_deferrer())]
        if self.wait and self.listen_notify:
            listener_coro = self.app.job_manager.listen_for_jobs(
                event=notify_event,
                queues=self.queues,
            )
            side_tasks.append(asyncio.create_task(listener_coro, name="listener"))

        try:
            context = contextlib.nullcontext()
            if self.install_signal_handlers:
                context = signals.on_stop(self.stop)
            with context:
                """Processes jobs until cancelled or until there is no more available job (wait=False)"""
                while True:
                    out_of_job = None
                    while not out_of_job:
                        # acquire job_semaphore so that a new job is not fetched if maximum concurrency is reached
                        async with job_semaphore:
                            job = await self.app.job_manager.fetch_job(
                                queues=self.queues
                            )
                        if job:
                            # job_semaphore should be acquired straight because it is
                            # only acquired when not at full capacity at this time
                            # however, shield it from cancellation in the unlikely event the worker
                            # is cancelled at that precise time to not abandon the job
                            await asyncio.shield(job_semaphore.acquire())

                            job_context = self.base_context.evolve(
                                additional_context=self.base_context.additional_context.copy(),
                                job=job,
                                task=self.app.tasks.get(job.task_name),
                            )
                            job_task = asyncio.create_task(
                                self._process_job(job_context)
                            )
                            running_jobs[job_context] = job_task

                            def on_job_complete(
                                job_context: JobContext, _: asyncio.Task
                            ):
                                del running_jobs[job_context]
                                job_semaphore.release()

                            job_task.add_done_callback(
                                functools.partial(on_job_complete, job_context)
                            )
                        else:
                            out_of_job = True
                    if out_of_job:
                        if not self.wait:
                            self.logger.info(
                                "No job found. Stopping worker because wait=False",
                                extra=self.base_context.log_extra(
                                    action="stop_worker", queues=self.queues
                                ),
                            )
                            break
                        try:
                            # awaken when a notification that a new job is available
                            # or after specified polling interval elapses
                            notify_event.clear()
                            await asyncio.wait_for(
                                notify_event.wait(), timeout=self.polling_interval
                            )

                        except asyncio.TimeoutError:
                            # polling interval has passed, resume loop and attempt to fetch a job
                            pass

        finally:
            await utils.cancel_and_capture_errors(side_tasks)

            now = time.time()
            for job_context in running_jobs.keys():
                self.logger.info(
                    "Waiting for job to finish: "
                    + job_context.job_description(current_timestamp=now),
                    extra=job_context.log_extra(action="ending_job"),
                )

            # wait for any in progress job to complete processing
            # use return_exceptions to not cancel other job tasks if one was to fail
            await asyncio.gather(
                *(task for task in running_jobs.values()), return_exceptions=True
            )
            self.logger.info(
                f"Stopped worker on {self.base_context.queues_display}",
                extra=self.base_context.log_extra(
                    action="stop_worker", queues=self.queues
                ),
            )
