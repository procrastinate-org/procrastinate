import cmd
from typing import Dict

from procrastinate import jobs, manager, utils


def parse_argument(arg: str) -> Dict[str, str]:
    splitted_args = (item.partition("=") for item in arg.split())
    return {key: value for key, _, value in splitted_args}


def print_job(job: jobs.Job, details: bool = False) -> None:
    job_dict = job.asdict()
    msg = f"#{job_dict['id']} {job_dict['task_name']} on {job_dict['queue']} "
    msg += f"- [{job_dict['status']}]"
    if details:
        msg += (
            f" (attempts={job_dict['attempts']}, "
            f"scheduled_at={job_dict['scheduled_at']}, args={job_dict['task_kwargs']}, "
            f"lock={job_dict['lock']})"
        )
    print(msg)


class ProcrastinateShell(cmd.Cmd):
    intro = "Welcome to the procrastinate shell.   Type help or ? to list commands.\n"
    prompt = "procrastinate> "

    def __init__(self, job_manager: manager.JobManager):
        super().__init__()
        self.job_manager = job_manager

    def do_EOF(self, _) -> bool:
        "Exit procrastinate shell."
        return True

    do_exit = do_EOF

    def do_list_jobs(self, arg: str) -> None:
        """
        List jobs.
        Usage: list_jobs [id=ID] [queue=QUEUE_NAME] [task=TASK_NAME] [status=STATUS]
                         [lock=LOCK] [queueing_lock=QUEUEING_LOCK] [details]

        Jobs can be filtered by id, queue name, task name, status and lock.
        Use the details argument to get more info about jobs.

        Example: list_jobs queue=default task=sums status=failed details
        """
        kwargs = parse_argument(arg)
        details = kwargs.pop("details", None) is not None
        for job in self.job_manager.list_jobs(**kwargs):  # type: ignore
            print_job(job, details=details)

    def do_list_queues(self, arg: str) -> None:
        """
        List queues: get queue names and number of jobs per queue.
        Usage: list_queues [queue=QUEUE_NAME] [task=TASK_NAME] [status=STATUS]
                           [lock=LOCK]

        Jobs can be filtered by queue name, task name, status and lock.

        Example: list_queues task=sums status=failed
        """
        kwargs = parse_argument(arg)
        for queue in self.job_manager.list_queues(**kwargs):  # type: ignore
            print(
                f"{queue['name']}: {queue['jobs_count']} jobs ("
                f"todo: {queue['todo']}, "
                f"doing: {queue['doing']}, "
                f"succeeded: {queue['succeeded']}, "
                f"failed: {queue['failed']})"
            )

    def do_list_tasks(self, arg: str) -> None:
        """
        List tasks: get task names and number of jobs per task.
        Usage: list_tasks [queue=QUEUE_NAME] [task=TASK_NAME] [status=STATUS]
                          [lock=LOCK]

        Jobs can be filtered by queue name, task name, status and lock.

        Example: list_tasks queue=default status=failed
        """
        kwargs = parse_argument(arg)
        for task in self.job_manager.list_tasks(**kwargs):  # type: ignore
            print(
                f"{task['name']}: {task['jobs_count']} jobs ("
                f"todo: {task['todo']}, "
                f"doing: {task['doing']}, "
                f"succeeded: {task['succeeded']}, "
                f"failed: {task['failed']})"
            )

    def do_list_locks(self, arg: str) -> None:
        """
        List locks: get lock names and number of jobs per task.
        Usage: list_locks [queue=QUEUE_NAME] [task=TASK_NAME] [status=STATUS]
                          [lock=LOCK]

        Jobs can be filtered by queue name, task name, status and lock.

        Example: list_locks queue=default status=todo
        """
        kwargs = parse_argument(arg)
        for lock in self.job_manager.list_locks(**kwargs):  # type: ignore
            print(
                f"{lock['name']}: {lock['jobs_count']} jobs ("
                f"todo: {lock['todo']}, "
                f"doing: {lock['doing']}, "
                f"succeeded: {lock['succeeded']}, "
                f"failed: {lock['failed']})"
            )

    def do_retry(self, arg: str) -> None:
        """
        Retry a specific job (reset its status to todo).
        Usage: retry JOB_ID

        JOB_ID is the id (numeric) of the job.

        Example: retry 2
        """
        job_id = int(arg)
        self.job_manager.retry_job_by_id(  # type: ignore
            job_id=job_id, retry_at=utils.utcnow().replace(microsecond=0)
        )
        (job,) = self.job_manager.list_jobs(id=job_id)  # type: ignore
        print_job(job)

    def do_cancel(self, arg: str) -> None:
        """
        Cancel a specific job (set its status to failed).
        Usage: cancel JOB_ID

        JOB_ID is the id (numeric) of the job.

        Example: cancel 3
        """
        job_id = int(arg)
        self.job_manager.finish_job_by_id(  # type: ignore
            job_id=job_id, status=jobs.Status.FAILED, delete_job=False
        )
        (job,) = self.job_manager.list_jobs(id=job_id)  # type: ignore
        print_job(job)
