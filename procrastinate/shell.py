import cmd

from procrastinate import admin


def parse_argument(arg):
    splitted_args = (item.partition("=") for item in arg.split())
    return {key: value for key, _, value in splitted_args}


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
        for job in self.admin.list_jobs(**kwargs):
            print(job)

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
