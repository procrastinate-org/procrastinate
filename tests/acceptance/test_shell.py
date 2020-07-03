import subprocess

import pytest


@pytest.fixture
def shell(process_env):
    return subprocess.Popen(
        ["procrastinate", "shell"],
        env=process_env(),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",
    )


def test_shell(shell, defer):
    defer("sum_task", a=5, b=7)
    defer("sum_task", ["--lock=lock"], a=3, b=8)
    defer("sum_task", ["--queue=other", "--lock=lock"], a=1, b=2)
    defer("increment_task", [], a=5)

    print("cancel 2", file=shell.stdin)
    print("cancel 3", file=shell.stdin)
    print("cancel 4", file=shell.stdin)
    print("retry 3", file=shell.stdin)

    print("list_jobs", file=shell.stdin)
    print("list_jobs queue=other details", file=shell.stdin)
    print("list_queues", file=shell.stdin)
    print("list_tasks", file=shell.stdin)

    print("exit", file=shell.stdin)
    shell.stdin.close()

    assert shell.stdout.readlines() == [
        "Welcome to the procrastinate shell.   Type help or ? to list commands.\n",
        "\n",
        # cancel / retry
        "procrastinate> #2 tests.acceptance.app.sum_task on default - [failed]\n",
        "procrastinate> #3 tests.acceptance.app.sum_task on other - [failed]\n",
        "procrastinate> #4 tests.acceptance.app.increment_task on default - [failed]\n",
        "procrastinate> #3 tests.acceptance.app.sum_task on other - [todo]\n",
        # list_jobs
        "procrastinate> #1 tests.acceptance.app.sum_task on default - [todo]\n",
        "#2 tests.acceptance.app.sum_task on default - [failed]\n",
        "#3 tests.acceptance.app.sum_task on other - [todo]\n",
        "#4 tests.acceptance.app.increment_task on default - [failed]\n",
        # list_jobs queue=other details
        "procrastinate> #3 tests.acceptance.app.sum_task on other - [todo] "
        "(attempts=0, scheduled_at=None, args={'a': 1, 'b': 2}, lock=lock)\n",
        # list_queues
        "procrastinate> default: 3 jobs (todo: 1, succeeded: 0, failed: 2)\n",
        "other: 1 jobs (todo: 1, succeeded: 0, failed: 0)\n",
        # list_tasks
        "procrastinate> tests.acceptance.app.increment_task: 1 jobs "
        "(todo: 0, succeeded: 0, failed: 1)\n",
        "tests.acceptance.app.sum_task: 3 jobs " "(todo: 2, succeeded: 0, failed: 1)\n",
        #
        "procrastinate> ",
    ]
