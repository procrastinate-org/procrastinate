from __future__ import annotations

import asyncio
import contextlib
import logging
import time
from typing import Any, Iterable

from procrastinate import signals, utils
from procrastinate.app import App
from procrastinate.exceptions import TaskNotFound
from procrastinate.job_context import JobContext
from procrastinate.job_processor import JobProcessor
from procrastinate.jobs import DeleteJobCondition, Job
from procrastinate.periodic import PeriodicDeferrer
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
        self.delete_jobs = delete_jobs
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

    async def run(self):
        self._run_task = asyncio.current_task()
        notify_event = asyncio.Event()

        self.logger.info(
            f"Starting worker on {self.base_context.queues_display}",
            extra=self.base_context.log_extra(
                action="start_worker", queues=self.queues
            ),
        )

        job_queue: asyncio.Queue[Job] = asyncio.Queue(self.concurrency)
        job_semaphore = asyncio.Semaphore(self.concurrency)
        fetch_job_condition = asyncio.Condition()
        job_processors = [
            JobProcessor(
                task_registry=self.app.tasks,
                base_context=self.base_context,
                delete_jobs=self.delete_jobs,
                job_manager=self.app.job_manager,
                job_queue=job_queue,
                job_semaphore=job_semaphore,
                fetch_job_condition=fetch_job_condition,
                worker_id=worker_id,
                logger=self.logger,
            )
            for worker_id in range(self.concurrency)
        ]

        job_processors_task = asyncio.gather(*(p.run() for p in job_processors))
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
                        # we don't want to fetch any new job if all processors are busy
                        # or when the queue is already full
                        # it is preferable to let any other procrastinate worker process handle those
                        # jobs until we are ready to process more
                        async with fetch_job_condition:
                            await fetch_job_condition.wait_for(
                                lambda: not job_queue.full()
                                and not job_semaphore.locked()
                            )
                        job = await self.app.job_manager.fetch_job(queues=self.queues)
                        if job:
                            # once a job has been fetched, we don't want to be cancelled until we put the job
                            # in the queue. For this reason, we prefer job_queue.put_nowait to job_queue.put
                            #
                            # The cleanup process ensures any job in the queue is awaited.
                            #
                            # We also made sure the queue is not full before fetching the job.
                            # Given only this worker adds to the queue, we don't need to worry about QueueFull being raised
                            job_queue.put_nowait(job)
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
                            # no more job to fetch and asked not to wait, exiting the loop
                            break
                        try:
                            # wait until notified a new job is available or until polling interval
                            notify_event.clear()
                            await asyncio.wait_for(
                                notify_event.wait(), timeout=self.polling_interval
                            )

                        except asyncio.TimeoutError:
                            # catch asyncio.TimeoutError and not TimeoutError as long as Python 3.10 and under are supported

                            # polling interval has passed, resume loop and attempt to fetch a job
                            pass

        finally:
            await utils.cancel_and_capture_errors(side_tasks)

            pending_job_contexts = [
                processor.job_context
                for processor in job_processors
                if processor.job_context
            ]

            now = time.time()
            for context in pending_job_contexts:
                self.logger.info(
                    "Waiting for job to finish: "
                    + context.job_description(current_timestamp=now),
                    extra=context.log_extra(action="ending_job"),
                )

            # make sure any job in progress or still in the queue is given time to be processed
            await job_queue.join()
            job_processors_task.cancel()
            job_processors_task.add_done_callback(
                lambda fut: self.logger.info(
                    f"Stopped worker on {self.base_context.queues_display}",
                    extra=self.base_context.log_extra(
                        action="stop_worker", queues=self.queues
                    ),
                )
            )

            try:
                await job_processors_task
            except asyncio.CancelledError:
                # if we didn't initiate the cancellation ourselves, bubble up the cancelled error
                if self._run_task and self._run_task.cancelled():
                    raise
