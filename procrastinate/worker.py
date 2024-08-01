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
        shutdown_timeout: float | None = None,
        listen_notify: bool = True,
        delete_jobs: str | jobs.DeleteJobCondition | None = None,
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
        ) or jobs.DeleteJobCondition.NEVER
        self.additional_context = additional_context
        self.install_signal_handlers = install_signal_handlers

        if self.worker_name:
            self.logger = logger.getChild(self.worker_name)
        else:
            self.logger = logger

        self._loop_task: asyncio.Future | None = None
        self._notify_event = asyncio.Event()
        self._running_jobs: dict[asyncio.Task, job_context.JobContext] = {}
        self._job_semaphore = asyncio.Semaphore(self.concurrency)
        self._stop_event = asyncio.Event()
        self.shutdown_timeout = shutdown_timeout

    def stop(self):
        if self._stop_event.is_set():
            return
        self.logger.info(
            "Stop requested",
            extra=self._log_extra(context=None, action="stopping_worker"),
        )

        self._stop_event.set()

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
        # in practice we should always have a start and end timestamp here
        # but in theory the JobResult class allows it to be None
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

            async def ensure_async() -> Callable[..., Awaitable]:
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

                return task_result

            job_result.result = await ensure_async()

        except BaseException as e:
            exc_info = e
            is_aborting = (
                (await self.app.job_manager.get_job_status_async(job_id=job.id))
                == jobs.Status.ABORTING
                if job.id
                else False
            )
            if not isinstance(e, exceptions.JobAborted) and not is_aborting:
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
        finally:
            job_result.end_timestamp = time.time()

            if isinstance(exc_info, exceptions.JobAborted) or isinstance(
                exc_info, asyncio.CancelledError
            ):
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
        """Fetch and process jobs until there is no job left or asked to stop"""
        while not self._stop_event.is_set():
            acquire_sem_task = asyncio.create_task(self._job_semaphore.acquire())
            job = None
            try:
                await utils.wait_any(acquire_sem_task, self._stop_event.wait())
                if self._stop_event.is_set():
                    break
                job = await self.app.job_manager.fetch_job(queues=self.queues)
            finally:
                if (not job or self._stop_event.is_set()) and acquire_sem_task.done():
                    self._job_semaphore.release()
                self._notify_event.clear()

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
            job_task = asyncio.create_task(
                self._process_job(context),
                name=f"process job {job.task_name}[{job.id}]",
            )
            self._running_jobs[job_task] = context

            def on_job_complete(task: asyncio.Task):
                del self._running_jobs[task]
                self._job_semaphore.release()

            job_task.add_done_callback(on_job_complete)

    async def run(self):
        """
        Run the worker
        This will run forever until asked to stop/cancelled, or until no more job is available is configured not to wait
        """
        self.run_task = asyncio.current_task()
        loop_task = asyncio.create_task(self._run_loop())

        try:
            # shield the loop task from cancellation
            # instead, a stop event is set to enable graceful shutdown
            await utils.wait_any(asyncio.shield(loop_task), self._stop_event.wait())
            if self._stop_event.is_set():
                try:
                    await asyncio.wait_for(loop_task, timeout=self.shutdown_timeout)
                except asyncio.TimeoutError:
                    pass
        except asyncio.CancelledError:
            self.stop()
            try:
                await asyncio.wait_for(loop_task, timeout=self.shutdown_timeout)
            except asyncio.TimeoutError:
                pass
            raise

    async def _shutdown(self, side_tasks: list[asyncio.Task]):
        """
        Gracefully shutdown the worker by cancelling side tasks
        and waiting for all pending jobs.
        """
        await utils.cancel_and_capture_errors(side_tasks)

        now = time.time()
        for context in self._running_jobs.values():
            self.logger.info(
                "Waiting for job to finish: "
                + context.job_description(current_timestamp=now),
                extra=self._log_extra(context=None, action="ending_job"),
            )

        # wait for any in progress job to complete processing
        # use return_exceptions to not cancel other job tasks if one was to fail
        await asyncio.gather(*self._running_jobs, return_exceptions=True)
        self.logger.info(
            f"Stopped worker on {utils.queues_display(self.queues)}",
            extra=self._log_extra(
                action="stop_worker", queues=self.queues, context=None
            ),
        )

    def _start_side_tasks(self) -> list[asyncio.Task]:
        """Start side tasks such as periodic deferrer and notification listener"""
        side_tasks = [asyncio.create_task(self.periodic_deferrer())]
        if self.wait and self.listen_notify:
            listener_coro = self.app.job_manager.listen_for_jobs(
                event=self._notify_event,
                queues=self.queues,
            )
            side_tasks.append(asyncio.create_task(listener_coro, name="listener"))
        return side_tasks

    async def _run_loop(self):
        """
        Run all side coroutines, then start fetching/processing jobs in a loop
        """
        self.logger.info(
            f"Starting worker on {utils.queues_display(self.queues)}",
            extra=self._log_extra(
                action="start_worker", context=None, queues=self.queues
            ),
        )
        self._notify_event.clear()
        self._stop_event.clear()
        self._running_jobs = {}
        self._job_semaphore = asyncio.Semaphore(self.concurrency)
        side_tasks = self._start_side_tasks()

        context = (
            signals.on_stop(self.stop)
            if self.install_signal_handlers
            else contextlib.nullcontext()
        )

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
                    self._stop_event.set()

                while not self._stop_event.is_set():
                    # wait for a new job notification, a stop even or the next polling interval
                    await utils.wait_any(
                        self._notify_event.wait(),
                        asyncio.sleep(self.polling_interval),
                        self._stop_event.wait(),
                    )
                    await self._fetch_and_process_jobs()
        finally:
            await self._shutdown(side_tasks=side_tasks)
