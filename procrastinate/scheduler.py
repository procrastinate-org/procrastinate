import logging
from apscheduler.schedulers.blocking import BlockingScheduler

from procrastinate import app, exceptions

logger = logging.getLogger(__name__)


class Scheduler:
    def __init__(self, app: app.App):
        self.app = app
        self.app.perform_import_paths()

    def run(self) -> None:
        logger.info("Setting up scheduled jobs…")
        if not self.app.schedule:
            raise exceptions.SchedulerConfigError("No scheduled jobs found")

        sched = BlockingScheduler()
        for row in self.app.schedule:
            try:
                job_id = row["job"]
            except KeyError:
                raise exceptions.SchedulerConfigError("Schedule entry is missing job")

            try:
                job = self.app.tasks[job_id]
            except KeyError:
                raise exceptions.SchedulerConfigError("Invalid job {}".format(job_id))

            args = row.get("args", [])
            kwargs = row.get("kwargs", {})
            cron = row["cron"]
            if not cron:
                raise exceptions.SchedulerConfigError(
                    "Missing cron configuration for job {}".format(job_id)
                )

            sched.add_job(job.defer, args=args, kwargs=kwargs, trigger="cron", **cron)

        logger.info("Starting scheduler…")
        sched.start()
