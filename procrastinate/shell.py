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
                f"{queue['name']}: {queue['nb_jobs']} jobs ("
                f"todo: {queue['nb_todo']}, "
                f"succeeded: {queue['nb_succeeded']}, "
                f"failed: {queue['nb_failed']})"
            )

    def do_list_tasks(self, arg):
        kwargs = parse_argument(arg)
        for task in self.admin.list_tasks(**kwargs):
            print(
                f"{task['name']}: {task['nb_jobs']} jobs ("
                f"todo: {task['nb_todo']}, "
                f"succeeded: {task['nb_succeeded']}, "
                f"failed: {task['nb_failed']})"
            )

    def do_list_stalled_jobs(self, arg):
        kwargs = parse_argument(arg)
        for job in self.admin.list_jobs(status="doing", **kwargs):
            print(job)

    def do_list_error_jobs(self, arg):
        kwargs = parse_argument(arg)
        for job in self.admin.list_jobs(status="failed", **kwargs):
            print(job)

    def do_retry(self, arg):
        print_job(self.admin.set_job_status(arg, status="todo"))

    def do_discard(self, arg):
        print_job(self.admin.set_job_status(arg, status="failed"))
