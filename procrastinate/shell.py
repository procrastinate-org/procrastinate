import cmd

from procrastinate import admin


def parse_argument(arg):
    splitted_args = (item.partition("=") for item in arg.split())
    return {key: value for key, _, value in splitted_args}


def print_job(job, details=False):
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

    def do_EOF(self, _):
        "Exit procrastinate shell"
        return True

    do_exit = do_EOF

    def do_list_jobs(self, arg):
        kwargs = parse_argument(arg)
        details = kwargs.pop("details", None) is not None
        for job in self.admin.list_jobs(**kwargs):
            print_job(job, details=details)

    def do_list_queues(self, arg):
        kwargs = parse_argument(arg)
        for queue in self.admin.list_queues(**kwargs):
            print(
                f"{queue['name']}: {queue['jobs_count']} jobs ("
                f"todo: {queue['todo']}, "
                f"succeeded: {queue['succeeded']}, "
                f"failed: {queue['failed']})"
            )

    def do_list_tasks(self, arg):
        kwargs = parse_argument(arg)
        for task in self.admin.list_tasks(**kwargs):
            print(
                f"{task['name']}: {task['jobs_count']} jobs ("
                f"todo: {task['todo']}, "
                f"succeeded: {task['succeeded']}, "
                f"failed: {task['failed']})"
            )

    def do_retry(self, arg):
        print_job(self.admin.set_job_status(arg, status="todo"))

    def do_cancel(self, arg):
        print_job(self.admin.set_job_status(arg, status="failed"))
