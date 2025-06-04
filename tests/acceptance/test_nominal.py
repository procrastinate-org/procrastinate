from __future__ import annotations

import signal
import subprocess
import time
from typing import Protocol

import pytest


class RunningWorker(Protocol):
    def __call__(
        self, *args: str, name: str = "worker", app: str = "app"
    ) -> subprocess.Popen[str]: ...


class Worker(Protocol):
    def __call__(
        self, *args: str, sleep: int = 1, app: str = "app"
    ) -> tuple[str, str]: ...


@pytest.fixture
def worker(running_worker) -> Worker:
    def func(*queues, sleep=1, app="app"):
        process = running_worker(*queues, app=app)
        time.sleep(sleep)
        process.send_signal(signal.SIGINT)
        return process.communicate()

    return func


@pytest.fixture
def running_worker(process_env) -> RunningWorker:
    def func(*queues, name="worker", app="app"):
        return subprocess.Popen(
            [
                "procrastinate",
                "-vvv",
                "worker",
                f"--name={name}",
                "--queues",
                ",".join(queues),
            ],
            env=process_env(app=app),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8",
        )

    return func


@pytest.mark.parametrize("app", ["app", "app_aiopg"])
def test_nominal(defer, worker, app):
    from .param import Param

    defer("sum_task", a=5, b=7)
    defer("sum_task_param", p1=Param(3), p2=Param(4))
    defer("increment_task", a=3)

    stdout, stderr = worker(app=app)
    print(stdout, stderr)

    assert stdout.splitlines() == ["12", "7", "4"]
    assert stderr.startswith("DEBUG:procrastinate.")

    defer("product_task", a=5, b=4)

    stdout, stderr = worker("default", app=app)
    print(stdout, stderr)
    assert "20" not in stdout

    stdout, stderr = worker("product_queue", app=app)
    print(stdout, stderr)
    assert stdout.strip() == "20"

    defer("two_fails")
    stdout, stderr = worker(app=app, sleep=1.5)
    print(stdout, stderr)
    assert "Print something to stdout" in stdout
    assert stderr.count("Exception: This should fail") == 2

    defer("multiple_exception_failures")
    stdout, stderr = worker(app=app)
    print(stdout, stderr)
    assert (
        stdout
        == """Try 0
Try 1
Try 2
"""
    )

    assert stderr.count("Traceback (most recent call last)") == 3
    assert stderr.count("status: Error, to retry") == 2
    expected_log = "[6]() ended with status: Error"
    assert stderr.count(expected_log) == 3
    expected_log = "[6]() ended with status: Error, to retry"
    assert stderr.count(expected_log) == 2


@pytest.mark.parametrize("app", ["app", "app_aiopg"])
def test_priority(defer, worker, app):
    defer("sum_task", ["--priority", "5"], a=5, b=7)
    defer("sum_task", ["--priority", "7"], a=1, b=3)
    defer("sum_task", ["--priority", "6"], a=2, b=6)

    stdout, stderr = worker(app=app)
    print(stdout, stderr)

    assert stdout.splitlines() == ["4", "8", "12"]
    assert stderr.startswith("DEBUG:procrastinate.")


@pytest.mark.parametrize("app", ["app", "app_aiopg"])
def test_task_with_default_priority(defer, worker, app):
    defer("sum_task_with_default_priority", ["--priority", "3"], a=5, b=7)
    defer("sum_task_with_default_priority", ["--priority", "7"], a=1, b=3)
    defer("sum_task_with_default_priority", a=2, b=6)

    stdout, stderr = worker(app=app)
    print(stdout, stderr)

    assert stdout.splitlines() == ["4", "8", "12"]
    assert stderr.startswith("DEBUG:procrastinate.")


def test_lock(defer, running_worker):
    """
    In this test, we launch 2 workers in two parallel threads, and ask them
    both to process tasks with the same lock. We check that the second task is
    not started before the first one was finished, irrespective of the task priority
    """

    defer(
        "sleep_and_write",
        ["--lock", "a", "--priority", "1"],
        sleep=0.5,
        write_before="before-1",
        write_after="after-1",
    )

    # Run the 2 workers concurrently
    process1 = running_worker(name="worker1")
    process2 = running_worker(name="worker2")
    time.sleep(0.1)

    defer(
        "sleep_and_write",
        ["--lock", "a", "--priority", "2"],
        sleep=0.001,
        write_before="before-2",
        write_after="after-2",
    )

    time.sleep(1)
    # And stop them
    process1.send_signal(signal.SIGINT)
    process2.send_signal(signal.SIGINT)

    # Gather their stdout
    stdout1, stderr1 = process1.communicate()
    print(stderr1)
    stdout2, stderr2 = process2.communicate()
    print(stderr2)
    stdout = stdout1 + stdout2

    # Sort the interesting lines by timestamp to reconstitute a consistent view
    lines = dict(
        line.split()[1:] for line in stdout.splitlines() if line.startswith("->")
    )
    sorted_lines = sorted(lines, key=lambda x: lines[x])

    # Check that it all happened in order
    assert sorted_lines == ["before-1", "after-1", "before-2", "after-2"]
    # If locks didnt work, we would have
    # ["before-1", "before-2", "after-2", "after-1"]


def test_queueing_lock(defer, running_worker):
    defer("sometask", ["--queueing-lock", "a"])
    defer("sometask", ["--queueing-lock", "b"])

    with pytest.raises(subprocess.CalledProcessError) as excinfo:
        defer("sometask", ["--queueing-lock", "a"])

    assert excinfo.value.returncode == 1

    with pytest.raises(subprocess.CalledProcessError) as excinfo:
        defer("sometask", ["--queueing-lock", "a"], app="app")

    defer("sometask", ["--queueing-lock", "c"], app="app")

    # This one doesn't raise
    defer("sometask", ["--queueing-lock", "a", "--ignore-already-enqueued"])
    defer(
        "sometask",
        ["--queueing-lock", "a", "--ignore-already-enqueued"],
        app="app",
    )


def test_periodic_deferrer(worker: Worker):
    # We're launching a worker that executes a periodic task every second, and
    # letting it run for 2.5 s. It should execute the task 3 times, and print to stdout:
    # 0 <priority> <timestamp>
    # 1 <priority> <timestamp + 1>
    # 2 <priority> <timestamp + 2>  (this one won't always be there)
    stdout, stderr = worker(app="cron_app", sleep=3)
    # This won't be visible unless the test fails
    print(stdout)
    print(stderr)

    results = [
        [int(a) for a in e[5:].split()]
        for e in stdout.splitlines()
        if e.startswith("tick ")
    ]
    assert [row[0] for row in results][:2] == [0, 1]
    assert [row[1] for row in results][:2] == [7, 7]
    assert results[1][2] == results[0][2] + 1


@pytest.mark.skip_before_version("3.2.3")
def test_priority_order(defer, worker):
    # Defer two jobs for the same task, one with higher priority
    defer("echo_task", ["--priority", "5", "--lock", "a"], value="low")
    defer("echo_task", ["--priority", "10", "--lock", "a"], value="high")

    stdout, stderr = worker()
    print(stdout, stderr)

    # The job with the highest priority ("high") should be processed first
    lines = stdout.splitlines()
    assert lines[0] == "high"
    assert lines[1] == "low"
