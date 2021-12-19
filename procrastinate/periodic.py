import asyncio
import functools
import logging
import sys
import time
from typing import Any, Dict, Iterable, List, Optional, Tuple

import attr
import croniter

from procrastinate import exceptions, manager, tasks

# The maximum delay after which tasks will be considered as
# outdated, and ignored.
MAX_DELAY = 60 * 10  # 10 minutes
# We'll always be oversleeping by this amount to avoid waking up too early for our
# tasks. This is, of course, the most important part of procrastinate ;)
MARGIN = 0.5  # seconds

logger = logging.getLogger(__name__)

if sys.version_info < (3, 8):
    cached_property = property
else:
    cached_property = functools.cached_property


@attr.dataclass(frozen=True)
class PeriodicTask:
    task: tasks.Task
    cron: str
    periodic_id: str
    configure_kwargs: Dict[str, Any]

    @cached_property
    def croniter(self) -> croniter.croniter:
        return croniter.croniter(self.cron)


TaskAtTime = Tuple[PeriodicTask, int]


class PeriodicDeferrer:
    def __init__(self, job_manager: manager.JobManager, max_delay: float = MAX_DELAY):
        self.periodic_tasks: List[PeriodicTask] = []
        self.job_manager = job_manager
        # {(task_name, periodic_id): defer_timestamp}
        self.last_defers: Dict[Tuple[str, str], int] = {}
        self.max_delay = max_delay

    def periodic_decorator(self, cron: str, periodic_id: str, **kwargs):
        """
        Decorator over a task definition that registers that task for periodic
        launch. This decorator should not be used directly, ``@app.periodic()`` is meant
        to be used instead.
        """

        def wrapper(task: tasks.Task):
            self.register_task(
                task=task, cron=cron, periodic_id=periodic_id, configure_kwargs=kwargs
            )
            return task

        return wrapper

    async def worker(self) -> None:
        """
        High-level command for the periodic deferrer. Launches the loop.
        """
        if not self.periodic_tasks:
            logger.info(
                "No periodic task found, periodic deferrer will not run.",
                extra={"action": "periodic_deferrer_no_task"},
            )
            return

        while True:
            now = time.time()
            await self.defer_jobs(jobs_to_defer=self.get_previous_tasks(at=now))
            await self.wait(next_tick=self.get_next_tick(at=now))

    # Internal methods

    def register_task(
        self,
        task: tasks.Task,
        cron: str,
        periodic_id: str,
        configure_kwargs: Dict[str, Any],
    ) -> PeriodicTask:
        if any(
            pt
            for pt in self.periodic_tasks
            if pt.task is task and pt.periodic_id == periodic_id
        ):
            raise exceptions.TaskAlreadyRegistered(
                "A periodic task was already registed with the same periodic_id "
                f"({periodic_id!r}). Please use a different periodic_id for multiple "
                "schedules of the same task."
            )

        logger.info(
            f"Registering task {task.name} with suffix {periodic_id} to run "
            f"periodically with cron {cron}",
            extra={
                "action": "registering_periodic_task",
                "task": task.name,
                "cron": cron,
                "periodic_id": periodic_id,
                "kwargs": str(configure_kwargs),
            },
        )

        periodic_task = PeriodicTask(
            task=task,
            cron=cron,
            periodic_id=periodic_id,
            configure_kwargs=configure_kwargs,
        )
        self.periodic_tasks.append(periodic_task)
        return periodic_task

    def get_next_tick(self, at: float):
        """
        Return the number of seconds to wait before the next periodic task needs to be
        deferred.
        If now is not passed, the current timestamp is used.
        """
        next_timestamp = min(
            pt.croniter.get_next(ret_type=float, start_time=at)  # type: ignore
            for pt in self.periodic_tasks
        )
        return next_timestamp - at

    def get_previous_tasks(self, at: float) -> Iterable[TaskAtTime]:
        """
        Return each periodic task that may not have been deferred yet, alongside with
        its scheduled time.
        Tasks that should have been deferred more than self.max_delay seconds ago are
        ignored.
        """
        for periodic_task in self.periodic_tasks:
            task = periodic_task.task
            identifier = (task.name, periodic_task.periodic_id)

            for timestamp in self.get_timestamps(
                periodic_task=periodic_task,
                since=self.last_defers.get(identifier),
                until=at,
            ):
                self.last_defers[identifier] = timestamp
                yield periodic_task, timestamp

    def get_timestamps(
        self, periodic_task: PeriodicTask, since: Optional[int], until: float
    ) -> Iterable[int]:
        cron_iterator = periodic_task.croniter
        if since:
            # For some reason, mypy can't wrap its head around this statement.
            # You're welcome to tell us why (or how to fix it).
            timestamp = cron_iterator.set_current(start_time=since)  # type: ignore
            while True:
                timestamp = round(cron_iterator.get_next(ret_type=float))
                if timestamp > until:
                    return
                yield timestamp

        else:
            cron_iterator.set_current(start_time=until)  # type: ignore
            timestamp = round(cron_iterator.get_prev(ret_type=float))
            delay = until - timestamp

            if delay > self.max_delay:
                logger.debug(
                    "Ignoring periodic task scheduled more than "
                    f"{self.max_delay} s ago ({delay:.0f} s)",
                    extra={
                        "action": "ignore_periodic_task",
                        "max_delay": self.max_delay,
                        "delay": delay,
                    },
                )
                return

            yield timestamp

    async def defer_jobs(self, jobs_to_defer: Iterable[TaskAtTime]) -> None:
        """
        Try deferring all tasks that might need deferring. The database will keep us
        from deferring the same task for the same scheduled time multiple times.
        """
        for periodic_task, timestamp in jobs_to_defer:
            task = periodic_task.task
            periodic_id = periodic_task.periodic_id
            configure_kwargs = periodic_task.configure_kwargs
            description = {
                "task_name": task.name,
                "periodic_id": periodic_id,
                "defer_timestamp": timestamp,
                "kwargs": configure_kwargs,
            }
            try:
                job_id = await self.job_manager.defer_periodic_job(
                    task=task,
                    periodic_id=periodic_id,
                    configure_kwargs=configure_kwargs,
                    defer_timestamp=timestamp,
                )
            except exceptions.AlreadyEnqueued:
                logger.debug(
                    f"Periodic job {task.name}(timestamp={timestamp}, "
                    f"periodic_id={periodic_id}) cannot be enqueued: there is already "
                    f"a job in the queue with the queueing lock {task.queueing_lock}",
                    extra={
                        "action": "skip_periodic_task_queueing_lock",
                        "queueing_lock": task.queueing_lock,
                        **description,
                    },
                )
                continue

            if job_id:
                logger.info(
                    f"Periodic task {task.name} deferred for timestamp "
                    f"{timestamp} with id {job_id}",
                    extra={
                        "action": "periodic_task_deferred",
                        "job_id": job_id,
                        **description,
                    },
                )
            else:
                logger.debug(
                    f"Periodic task {task.name} skipped: already "
                    f"deferred for timestamp {timestamp}",
                    extra={
                        "action": "periodic_task_already_deferred",
                        **description,
                    },
                )

    async def wait(self, next_tick: float) -> None:
        """
        Wait until it's time to defer new tasks.
        """
        logger.debug(
            f"Periodic deferrer waiting for next tasks to defer ({next_tick:.0f} s)",
            extra={"action": "wait_next_tick", "next_tick": next_tick},
        )

        await asyncio.sleep(next_tick + MARGIN)
