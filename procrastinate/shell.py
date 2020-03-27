import cmd

from procrastinate import admin
from procrastinate.utils import sync_await


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

    def do_list_jobs(self, _):
        for job in self.admin.list_jobs():
            print(job)

    def do_list_queues(self, _):
        for queue in self.admin.list_queues():
            print(
                f"{queue['name']}: {queue['nb_jobs']} jobs (todo: {queue['nb_todo']}, succeeded: {queue['nb_succeeded']}, failed: {queue['nb_failed']})"
            )

    def do_list_tasks(self, _):
        for task in self.admin.list_tasks():
            print(
                f"{task['name']}: {task['nb_jobs']} jobs (todo: {task['nb_todo']}, succeeded: {task['nb_succeeded']}, failed: {task['nb_failed']})"
            )
