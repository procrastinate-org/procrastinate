from __future__ import annotations

import asyncio

import pytest

from procrastinate import manager
from procrastinate import shell as shell_module

from .. import conftest


@pytest.fixture
def shell(connector):
    return shell_module.ProcrastinateShell(manager.JobManager(connector=connector))


def test_exit(shell):
    assert shell.do_exit("") is True


def test_EOF(shell):
    assert shell.do_EOF("") is True


def test_list_jobs(shell, connector, capsys):
    asyncio.run(
        connector.defer_job_one(
            "task1",
            0,
            "lock1",
            "queueing_lock1",
            {},
            conftest.aware_datetime(2000, 1, 1),
            "queue1",
        )
    )
    asyncio.run(
        connector.defer_job_one(
            "task2",
            0,
            "lock2",
            "queueing_lock2",
            {},
            conftest.aware_datetime(2000, 1, 1),
            "queue2",
        )
    )

    shell.do_list_jobs("")
    captured = capsys.readouterr()
    assert captured.out.splitlines() == [
        "#1 task1 on queue1 - [todo]",
        "#2 task2 on queue2 - [todo]",
    ]
    assert connector.queries == [
        (
            "list_jobs",
            {
                "id": None,
                "queue_name": None,
                "task_name": None,
                "queueing_lock": None,
                "lock": None,
                "status": None,
            },
        )
    ]


def test_list_jobs_filters(shell, connector, capsys):
    asyncio.run(
        connector.defer_job_one(
            "task1",
            0,
            "lock1",
            "queueing_lock1",
            {},
            conftest.aware_datetime(2000, 1, 1),
            "queue1",
        )
    )
    asyncio.run(
        connector.defer_job_one(
            "task2",
            0,
            "lock2",
            "queueing_lock2",
            {},
            conftest.aware_datetime(2000, 1, 1),
            "queue2",
        )
    )

    shell.do_list_jobs("id=2 queue=queue2 task=task2 lock=lock2 status=todo")
    captured = capsys.readouterr()
    assert captured.out.splitlines() == [
        "#2 task2 on queue2 - [todo]",
    ]
    assert connector.queries == [
        (
            "list_jobs",
            {
                "id": 2,
                "queue_name": "queue2",
                "task_name": "task2",
                "queueing_lock": None,
                "lock": "lock2",
                "status": "todo",
            },
        )
    ]


def test_list_jobs_details(shell, connector, capsys):
    asyncio.run(
        connector.defer_job_one(
            "task1",
            5,
            "lock1",
            "queueing_lock1",
            {"x": 11},
            conftest.aware_datetime(1000, 1, 1),
            "queue1",
        )
    )
    asyncio.run(
        connector.defer_job_one(
            "task2",
            7,
            "lock2",
            "queueing_lock2",
            {"y": 22},
            conftest.aware_datetime(2000, 1, 1),
            "queue2",
        )
    )

    shell.do_list_jobs("details")
    captured = capsys.readouterr()
    assert captured.out.splitlines() == [
        "#1 task1 on queue1 - [todo] (attempts=0, priority=5, scheduled_at=1000-01-01 "
        "00:00:00+00:00, args={'x': 11}, lock=lock1)",
        "#2 task2 on queue2 - [todo] (attempts=0, priority=7, scheduled_at=2000-01-01 "
        "00:00:00+00:00, args={'y': 22}, lock=lock2)",
    ]


def test_list_jobs_empty(shell, connector, capsys):
    shell.do_list_jobs("")
    captured = capsys.readouterr()
    assert captured.out == ""


def test_list_queues(shell, connector, capsys):
    asyncio.run(
        connector.defer_job_one("task1", 0, "lock1", "queueing_lock1", {}, 0, "queue1")
    )
    asyncio.run(
        connector.defer_job_one("task2", 0, "lock2", "queueing_lock2", {}, 0, "queue2")
    )

    shell.do_list_queues("")
    captured = capsys.readouterr()
    assert captured.out.splitlines() == [
        "queue1: 1 jobs (todo: 1, doing: 0, succeeded: 0, failed: 0, cancelled: 0, aborted: 0)",
        "queue2: 1 jobs (todo: 1, doing: 0, succeeded: 0, failed: 0, cancelled: 0, aborted: 0)",
    ]
    assert connector.queries == [
        (
            "list_queues",
            {"queue_name": None, "task_name": None, "lock": None, "status": None},
        )
    ]


def test_list_queues_filters(shell, connector, capsys):
    asyncio.run(
        connector.defer_job_one("task1", 0, "lock1", "queueing_lock1", {}, 0, "queue1")
    )
    asyncio.run(
        connector.defer_job_one("task2", 0, "lock2", "queueing_lock2", {}, 0, "queue2")
    )

    shell.do_list_queues("queue=queue2 task=task2 lock=lock2 status=todo")
    captured = capsys.readouterr()
    assert captured.out.splitlines() == [
        "queue2: 1 jobs (todo: 1, doing: 0, succeeded: 0, failed: 0, cancelled: 0, aborted: 0)",
    ]
    assert connector.queries == [
        (
            "list_queues",
            {
                "queue_name": "queue2",
                "task_name": "task2",
                "lock": "lock2",
                "status": "todo",
            },
        )
    ]


def test_list_queues_empty(shell, connector, capsys):
    shell.do_list_queues("")
    captured = capsys.readouterr()
    assert captured.out == ""


def test_list_tasks(shell, connector, capsys):
    asyncio.run(
        connector.defer_job_one("task1", 0, "lock1", "queueing_lock1", {}, 0, "queue1")
    )
    asyncio.run(
        connector.defer_job_one("task2", 0, "lock2", "queueing_lock2", {}, 0, "queue2")
    )

    shell.do_list_tasks("")
    captured = capsys.readouterr()
    assert captured.out.splitlines() == [
        "task1: 1 jobs (todo: 1, doing: 0, succeeded: 0, failed: 0, cancelled: 0, aborted: 0)",
        "task2: 1 jobs (todo: 1, doing: 0, succeeded: 0, failed: 0, cancelled: 0, aborted: 0)",
    ]
    assert connector.queries == [
        (
            "list_tasks",
            {"queue_name": None, "task_name": None, "lock": None, "status": None},
        )
    ]


def test_list_tasks_filters(shell, connector, capsys):
    asyncio.run(
        connector.defer_job_one("task1", 0, "lock1", "queueing_lock1", {}, 0, "queue1")
    )
    asyncio.run(
        connector.defer_job_one("task2", 0, "lock2", "queueing_lock2", {}, 0, "queue2")
    )

    shell.do_list_tasks("queue=queue2 task=task2 lock=lock2 status=todo")
    captured = capsys.readouterr()
    assert captured.out.splitlines() == [
        "task2: 1 jobs (todo: 1, doing: 0, succeeded: 0, failed: 0, cancelled: 0, aborted: 0)",
    ]
    assert connector.queries == [
        (
            "list_tasks",
            {
                "queue_name": "queue2",
                "task_name": "task2",
                "lock": "lock2",
                "status": "todo",
            },
        )
    ]


def test_list_tasks_empty(shell, connector, capsys):
    shell.do_list_tasks("")
    captured = capsys.readouterr()
    assert captured.out == ""


def test_list_locks(shell, connector, capsys):
    asyncio.run(
        connector.defer_job_one("task1", 0, "lock1", "queueing_lock1", {}, 0, "queue1")
    )
    asyncio.run(
        connector.defer_job_one("task2", 0, "lock2", "queueing_lock2", {}, 0, "queue2")
    )

    shell.do_list_locks("")
    captured = capsys.readouterr()
    assert captured.out.splitlines() == [
        "lock1: 1 jobs (todo: 1, doing: 0, succeeded: 0, failed: 0, cancelled: 0, aborted: 0)",
        "lock2: 1 jobs (todo: 1, doing: 0, succeeded: 0, failed: 0, cancelled: 0, aborted: 0)",
    ]
    assert connector.queries == [
        (
            "list_locks",
            {"queue_name": None, "task_name": None, "lock": None, "status": None},
        )
    ]


def test_list_locks_filters(shell, connector, capsys):
    asyncio.run(
        connector.defer_job_one("task1", 0, "lock1", "queueing_lock1", {}, 0, "queue1")
    )
    asyncio.run(
        connector.defer_job_one("task2", 0, "lock2", "queueing_lock2", {}, 0, "queue2")
    )

    shell.do_list_locks("queue=queue2 task=task2 lock=lock2 status=todo")
    captured = capsys.readouterr()
    assert captured.out.splitlines() == [
        "lock2: 1 jobs (todo: 1, doing: 0, succeeded: 0, failed: 0, cancelled: 0, aborted: 0)",
    ]
    assert connector.queries == [
        (
            "list_locks",
            {
                "queue_name": "queue2",
                "task_name": "task2",
                "lock": "lock2",
                "status": "todo",
            },
        )
    ]


def test_list_locks_empty(shell, connector, capsys):
    shell.do_list_locks("")
    captured = capsys.readouterr()
    assert captured.out == ""


def test_retry(shell, connector, capsys):
    asyncio.run(
        connector.defer_job_one(
            "task",
            0,
            "lock",
            "queueing_lock",
            {},
            conftest.aware_datetime(2000, 1, 1),
            "queue",
        )
    )
    asyncio.run(connector.set_job_status_run(1, "failed"))

    shell.do_list_jobs("id=1")
    captured = capsys.readouterr()
    assert captured.out.strip() == "#1 task on queue - [failed]"

    shell.do_retry("1")
    captured = capsys.readouterr()
    assert captured.out.strip() == "#1 task on queue - [todo]"


def test_cancel(shell, connector, capsys):
    asyncio.run(
        connector.defer_job_one(
            "task",
            0,
            "lock",
            "queueing_lock",
            {},
            conftest.aware_datetime(2000, 1, 1),
            "queue",
        )
    )

    shell.do_list_jobs("id=1")
    captured = capsys.readouterr()
    assert captured.out.strip() == "#1 task on queue - [todo]"

    shell.do_cancel("1")
    captured = capsys.readouterr()
    assert captured.out.strip() == "#1 task on queue - [cancelled]"
