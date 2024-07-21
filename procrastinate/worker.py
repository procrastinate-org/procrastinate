from __future__ import annotations

import asyncio
import contextlib
import functools
import inspect
import logging
import time
from typing import Any, Awaitable, Callable, Iterable

from procrastinate import (
    app,
    exceptions,
    job_context,
    jobs,
    periodic,
    retry,
    signals,
    tasks,
    types,
    utils,
)

logger = logging.getLogger(__name__)

WORKER_NAME = "worker"
WORKER_CONCURRENCY = 1  # maximum number of parallel jobs
POLLING_INTERVAL = 5.0  # seconds


class Worker:
    def __init__(
        self,
        app: app.App,
        queues: Iterable[str] | None = None,
        name: str | None = WORKER_NAME,
        concurrency: int = WORKER_CONCURRENCY,
        wait: bool = True,
        timeout: float = POLLING_INTERVAL,
        listen_notify: bool = True,
        delete_jobs: str
        | jobs.DeleteJobCondition = jobs.DeleteJobCondition.NEVER.value,
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
            jobs.DeleteJobCondition(delete_jobs)
            if isinstance(delete_jobs, str)
            else delete_jobs
        )
        self.additional_context = additional_context
        self.install_signal_handlers = install_signal_handlers

        if self.worker_name:
            self.logger = logger.getChild(self.worker_name)
        else:
            self.logger = logger

        self._run_task: asyncio.Task | None = None
        self.notify_event = asyncio.Event()
        self.running_jobs: dict[asyncio.Task, job_context.JobContext] = {}

    def stop(self):
        self.logger.info(
            "Stop requested",
            extra=self._log_extra(context=None, action="stopping_worker"),
        )

        if self._run_task:
            self._run_task.cancel()

    async def periodic_deferrer(self):
        deferrer = periodic.PeriodicDeferrer(
            registry=self.app.periodic_registry,
            **self.app.periodic_defaults,
        )
        return await deferrer.worker()

    def find_task(self, task_name: str) -> tasks.Task:
        try:
            return self.app.tasks[task_name]
        except KeyError as exc:
            raise exceptions.TaskNotFound from exc

    def _log_extra(
        self, action: str, context: job_context.JobContext | None, **kwargs: Any
    ) -> types.JSONDict:
        extra: types.JSONDict = {
            "action": action,
            "worker": {
                "name": self.worker_name,
                "job_id": context.job.id if context else None,
                "queues": self.queues,
            },
        }
        if context:
            extra["job"] = context.job.log_context()

        return {
            **extra,
            **(context.job_result if context else job_context.JobResult()).as_dict(),
            **kwargs,
        }

    async def _persist_job_status(
        self,
        job: jobs.Job,
        status: jobs.Status,
        retry_decision: retry.RetryDecision | None,
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
                jobs.DeleteJobCondition.ALWAYS: True,
                jobs.DeleteJobCondition.NEVER: False,
                jobs.DeleteJobCondition.SUCCESSFUL: status == jobs.Status.SUCCEEDED,
            }[self.delete_jobs]
            await self.app.job_manager.finish_job(
                job=job, status=status, delete_job=delete_job
            )

    def _log_job_outcome(
        self,
        status: jobs.Status,
        context: job_context.JobContext,
        job_retry: exceptions.JobRetry | None,
        exc_info: bool | BaseException = False,
    ):
        if status == jobs.Status.SUCCEEDED:
            log_action, log_title = "job_success", "Success"
        elif status == jobs.Status.ABORTED:
            log_action, log_title = "job_aborted", "Aborted"
        elif job_retry:
            log_action, log_title = "job_error_retry", "Error, to retry"
        else:
            log_action, log_title = "job_error", "Error"

        text = f"Job {context.job.call_string} ended with status: {log_title}, "
        if context.job_result.start_timestamp and context.job_result.end_timestamp:
            duration = (
                context.job_result.end_timestamp - context.job_result.start_timestamp
            )
            text += f"lasted {duration:.3f} s"
        if context.job_result.result:
            text += f" - Result: {context.job_result.result}"[:250]

        extra = self._log_extra(context=context, action=log_action)
        log_level = logging.ERROR if status == jobs.Status.FAILED else logging.INFO
        logger.log(log_level, text, extra=extra, exc_info=exc_info)

    async def _process_job(self, context: job_context.JobContext):
        """
        Processes a given job and persists its status
        """
        task = context.task
        job_retry = None
        exc_info = False
        retry_decision = None
        job = context.job
        assert job

        job_result = context.job_result
        job_result.start_timestamp = time.time()

        try:
            if not task:
                raise exceptions.TaskNotFound

            self.logger.debug(
                f"Loaded job info, about to start job {job.call_string}",
                extra=self._log_extra(context=context, action="loaded_job_info"),
            )

            self.logger.info(
                f"Starting job {job.call_string}",
                extra=self._log_extra(context=context, action="start_job"),
            )

            exc_info: bool | BaseException = False

            await_func: Callable[..., Awaitable]
            if inspect.iscoroutinefunction(task.func):
                await_func = task
            else:
                await_func = functools.partial(utils.sync_to_async, task)

            job_args = [context] if task.pass_context else []
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
            if not isinstance(e, exceptions.JobAborted):
                job_retry = (
                    task.get_retry_exception(exception=e, job=job) if task else None
                )
                retry_decision = job_retry.retry_decision if job_retry else None
                if isinstance(e, exceptions.TaskNotFound):
                    self.logger.exception(
                        f"Task was not found: {e}",
                        extra=self._log_extra(
                            context=context,
                            action="task_not_found",
                            exception=str(e),
                        ),
                    )
            if not isinstance(e, Exception):
                raise

        finally:
            job_result.end_timestamp = time.time()

            if isinstance(exc_info, exceptions.JobAborted):
                status = jobs.Status.ABORTED
            elif exc_info:
                status = jobs.Status.FAILED
            else:
                status = jobs.Status.SUCCEEDED

            self._log_job_outcome(
                status=status,
                context=context,
                job_retry=job_retry,
                exc_info=exc_info,
            )
            await self._persist_job_status(
                job=job, status=status, retry_decision=retry_decision
            )

            self.logger.debug(
                f"Acknowledged job completion {job.call_string}",
                extra=self._log_extra(
                    action="finish_task", context=context, status=status
                ),
            )

    async def _fetch_and_process_jobs(self):
        job_semaphore = asyncio.Semaphore(self.concurrency)
        """Keeps in fetching and processing jobs until there are no job left to process"""
        while True:
            await job_semaphore.acquire()
            try:
                job = await self.app.job_manager.fetch_job(queues=self.queues)
            except BaseException:
                job_semaphore.release()
                raise

            if not job:
                break

            context = job_context.JobContext(
                app=self.app,
                worker_name=self.worker_name,
                worker_queues=self.queues,
                additional_context=self.additional_context.copy()
                if self.additional_context
                else {},
                job=job,
                task=self.app.tasks.get(job.task_name),
            )
            job_task = asyncio.create_task(self._process_job(context))
            self.running_jobs[job_task] = context

            def on_job_complete(task: asyncio.Task):
                del self.running_jobs[task]
                job_semaphore.release()

            job_task.add_done_callback(on_job_complete)

    async def _wait_for_job(self):
        self.notify_event.clear()
        try:
            # awaken when a notification that a new job is available
            # or after specified polling interval elapses
            await asyncio.wait_for(
                self.notify_event.wait(), timeout=self.polling_interval
            )

        except asyncio.TimeoutError:
            # polling interval has passed, resume loop and attempt to fetch a job
            pass

    async def run(self):
        self._run_task = asyncio.current_task()

        self.logger.info(
            f"Starting worker on {utils.queues_display(self.queues)}",
            extra=self._log_extra(
                action="start_worker", context=None, queues=self.queues
            ),
        )

        self.running_jobs = {}
        side_tasks = [asyncio.create_task(self.periodic_deferrer())]
        if self.wait and self.listen_notify:
            listener_coro = self.app.job_manager.listen_for_jobs(
                event=self.notify_event,
                queues=self.queues,
            )
            side_tasks.append(asyncio.create_task(listener_coro, name="listener"))

        context = contextlib.nullcontext()
        if self.install_signal_handlers:
            context = signals.on_stop(self.stop)

        try:
            with context:
                await self._fetch_and_process_jobs()
                if not self.wait:
                    self.logger.info(
                        "No job found. Stopping worker because wait=False",
                        extra=self._log_extra(
                            context=None,
                            action="stop_worker",
                            queues=self.queues,
                        ),
                    )
                    return

                while True:
                    await self._wait_for_job()
                    await self._fetch_and_process_jobs()
        finally:
            await utils.cancel_and_capture_errors(side_tasks)

            now = time.time()
            for context in self.running_jobs.values():
                self.logger.info(
                    "Waiting for job to finish: "
                    + context.job_description(current_timestamp=now),
                    extra=self._log_extra(context=None, action="ending_job"),
                )

            # wait for any in progress job to complete processing
            # use return_exceptions to not cancel other job tasks if one was to fail
            await asyncio.gather(
                *(task for task in self.running_jobs.keys()), return_exceptions=True
            )
            self.logger.info(
                f"Stopped worker on {utils.queues_display(self.queues)}",
                extra=self._log_extra(
                    action="stop_worker", queues=self.queues, context=None
                ),
            )
