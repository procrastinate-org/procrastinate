import asyncio
import logging
import time
import functools
from typing import Iterable, List, Tuple, Dict, Optional

import attr
import croniter

from procrastinate import store, tasks

# The maximum delay after which tasks will be considered as
# too late, and ignored.
MAX_DELAY = 60 * 10  # 10 minutes
# We'll always be oversleeping by this amount to avoid waking up too early for our
# tasks. This is, of course, the most important part of procrastinate ;)
MARGIN = 0.5  # seconds

logger = logging.getLogger(__name__)

TaskAtTime = Tuple[tasks.Task, int]


@attr.dataclass(frozen=True)
class PeriodicTask:
    task: tasks.Task
    cron: str

    @functools.lru_cache(maxsize=1)
    def croniter(self) -> croniter.croniter:
        return croniter.croniter(self.cron)


class Scheduler:
    def __init__(self, job_store: store.JobStore, max_delay: float = MAX_DELAY):
        self.periodic_tasks: List[PeriodicTask] = []
        self.job_store = job_store
        self.last_schedules_for_task: Dict[str, int] = {}
        self.max_delay = max_delay

    def schedule_decorator(self, cron: str):
        """
        Decorator over a task definition that will reegister that task for periodic
        launch. This decorator should not be use directly, ``@app.schedule()`` is meant
        to be used instead.
        """

        def wrapper(task: tasks.Task):
            self.register_task(task=task, cron=cron)
            return task

        return wrapper

    async def worker(self) -> None:
        """
        High level command for the scheduler. Launches the scheduling loop.
        """
        if not self.periodic_tasks:
            logger.info(
                "No periodic task found, scheduler will not run.",
                extra={"action": "scheduler_no_task"},
            )
            return

        while True:
            await self.defer_jobs(jobs_to_defer=self.get_previous_tasks())
            await self.wait(next_tick=self.get_next_tick())

    # Internal methods

    def register_task(self, task: tasks.Task, cron: str) -> PeriodicTask:
        logger.info(
            f"Registring task {task.name} to run periodically with cron {cron}",
            extra={
                "action": "registering_periodic_task",
                "task": task.name,
                "cron": cron,
            },
        )
        periodic_task = PeriodicTask(task=task, cron=cron)
        self.periodic_tasks.append(periodic_task)
        return periodic_task

    def get_next_tick(self, now: Optional[float] = None):
        """
        Return the number of seconds to wait before the next scheduled task needs to be
        deferred.
        If now is not passed, the current timestamp is used.
        """
        now = now if now is not None else time.time()
        next_timestamp = min(
            pt.croniter().get_next(ret_type=float, start_time=now)  # type: ignore
            for pt in self.periodic_tasks
        )
        return next_timestamp - now

    def get_previous_tasks(self, now: Optional[float] = None) -> Iterable[TaskAtTime]:
        """
        Return each periodic task that may not have been defered yet, alongside with
        its scheduled time.
        Tasks that should have been defered more than self.max_delay seconds ago are
        ignored.
        """
        now = now if now is not None else time.time()

        known_schedule_keys = set(self.last_schedules_for_task.items())
        for periodic_task in self.periodic_tasks:
            task = periodic_task.task
            name = task.name
            cron_iterator = periodic_task.croniter()
            # For some reason, mypy can't wrap its head around this statement.
            # You're welcome to tell me why (or how to fix it).
            cron_iterator.set_current(start_time=now)  # type: ignore
            previous_time = round(cron_iterator.get_prev(ret_type=float))
            schedule_key = (name, previous_time)
            if schedule_key in known_schedule_keys:
                continue
            delay = now - previous_time
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
                continue

            self.last_schedules_for_task[name] = previous_time
            yield task, previous_time

    async def defer_jobs(self, jobs_to_defer: Iterable[TaskAtTime]) -> None:
        """
        Try deferring all tasks that might need defering. The database will keep us from
        deferring the same task for the same schedule time multiple times.
        """
        for task, timestamp in jobs_to_defer:
            job_id = await self.job_store.defer_periodic_job(
                task=task, schedule_timestamp=timestamp
            )
            if job_id:
                logger.info(
                    f"Periodic task {task.name} deferred for timestamp "
                    f"{timestamp} with id {job_id}",
                    extra={
                        "action": "periodic_task_deferred",
                        "task": task.name,
                        "timestamp": timestamp,
                        "job_id": job_id,
                    },
                )
            else:
                logger.debug(
                    f"Periodic task {task.name} skipped: already "
                    f"deferred for timestamp {timestamp}",
                    extra={
                        "action": "periodic_task_already_deferred",
                        "task": task.name,
                        "timestamp": timestamp,
                    },
                )

    async def wait(self, next_tick: float) -> None:
        """
        Wait until it's time to defer new tasks.
        """
        logger.debug(
            f"Scheduler waiting for next task to schedule ({next_tick:.0f} s)",
            extra={"action": "wait_next_tick", "next_tick": next_tick},
        )

        await asyncio.sleep(next_tick + MARGIN)
