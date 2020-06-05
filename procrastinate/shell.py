import cmd
from typing import Any, Dict

from procrastinate import admin


def parse_argument(arg: str) -> Dict[str, str]:
    splitted_args = (item.partition("=") for item in arg.split())
    return {key: value for key, _, value in splitted_args}


def print_job(job: Dict[str, Any], details: bool = False) -> None:
    msg = f"#{job['id']} {job['task']} on {job['queue']} - [{job['status']}]"
    if details:
        msg += (
            f" (attempts={job['attempts']}, "
            f"scheduled_at={job['scheduled_at']}, args={job['args']}, "
            f"lock={job['lock']})"
        )
    print(msg)


class ProcrastinateShell(cmd.Cmd):
    intro = "Welcome to the procrastinate shell.   Type help or ? to list commands.\n"
    prompt = "procrastinate> "

    def __init__(self, admin: admin.Admin):
        super().__init__()
        self.admin = admin

    def do_EOF(self, _) -> bool:
        "Exit procrastinate shell."
        return True

    do_exit = do_EOF

    def do_list_jobs(self, arg: str) -> None:
        """
        List procrastinate jobs.
        Usage: list_jobs [id=ID] [queue=QUEUE_NAME] [task=TASK_NAME] [status=STATUS]
                         [lock=LOCK] [queueing_lock=QUEUEING_LOCK] [details]

        Jobs can be filtered by id, queue name, task name, status and lock.
        Use the details argument to get more info about jobs.

        Example: list_jobs queue=default task=sums status=failed details
        """
        kwargs = parse_argument(arg)
        details = kwargs.pop("details", None) is not None
        for job in self.admin.list_jobs(**kwargs):  # type: ignore
            print_job(job, details=details)

    def do_list_queues(self, arg: str) -> None:
        """
        List procrastinate queues: get queues names and number of jobs per queue.
        Usage: list_queues [queue=QUEUE_NAME] [task=TASK_NAME] [status=STATUS]
                           [lock=LOCK]

        Jobs can be filtered by queue name, task name, status and lock.

        Example: list_queues task=sums status=failed
        """
        kwargs = parse_argument(arg)
        for queue in self.admin.list_queues(**kwargs):  # type: ignore
            print(
                f"{queue['name']}: {queue['jobs_count']} jobs ("
                f"todo: {queue['todo']}, "
                f"succeeded: {queue['succeeded']}, "
                f"failed: {queue['failed']})"
            )

    def do_list_tasks(self, arg: str) -> None:
        """
        List procrastinate tasks: get tasks names and number of jobs per task.
        Usage: list_tasks [queue=QUEUE_NAME] [task=TASK_NAME] [status=STATUS]
                          [lock=LOCK]

        Jobs can be filtered by queue name, task name, status and lock.

        Example: list_queues queue=default status=failed
        """
        kwargs = parse_argument(arg)
        for task in self.admin.list_tasks(**kwargs):  # type: ignore
            print(
                f"{task['name']}: {task['jobs_count']} jobs ("
                f"todo: {task['todo']}, "
                f"succeeded: {task['succeeded']}, "
                f"failed: {task['failed']})"
            )

    def do_retry(self, arg: str) -> None:
        """
        Retry a specific job (reset its status to todo).
        Usage: retry JOB_ID

        JOB_ID is the id (numeric) of the job.

        Example: retry 2
        """
        print_job(self.admin.set_job_status(arg, status="todo"))  # type: ignore

    def do_cancel(self, arg: str) -> None:
        """
        Cancel a specific job (set its status to failed).
        Usage: cancel JOB_ID

        JOB_ID is the id (numeric) of the job.

        Example: cancel 3
        """
        print_job(self.admin.set_job_status(arg, status="failed"))  # type: ignore
