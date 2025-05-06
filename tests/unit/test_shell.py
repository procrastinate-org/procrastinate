from __future__ import annotations

import pytest

from procrastinate import manager, testing, utils
from procrastinate import shell as shell_module
from procrastinate import types as t

from .. import conftest


@pytest.fixture
def shell(connector: testing.InMemoryConnector):
    return shell_module.ProcrastinateShell(manager.JobManager(connector=connector))


def test_exit(shell: shell_module.ProcrastinateShell):
    assert shell.do_exit("") is True


def test_EOF(shell: shell_module.ProcrastinateShell):
    assert shell.do_EOF("") is True


async def test_list_jobs(
    shell: shell_module.ProcrastinateShell,
    connector: testing.InMemoryConnector,
    capsys: pytest.CaptureFixture,
):
    await connector.defer_jobs_all(
        [
            t.JobToDefer(
                queue_name="queue1",
                task_name="task1",
                priority=0,
                lock="lock1",
                queueing_lock="queueing_lock1",
                args={},
                scheduled_at=conftest.aware_datetime(2000, 1, 1),
            ),
            t.JobToDefer(
                queue_name="queue2",
                task_name="task2",
                priority=0,
                lock="lock2",
                queueing_lock="queueing_lock2",
                args={},
                scheduled_at=conftest.aware_datetime(2000, 1, 1),
            ),
        ]
    )

    await utils.sync_to_async(shell.do_list_jobs, "")
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
                "worker_id": None,
            },
        )
    ]


async def test_list_jobs_filters(
    shell: shell_module.ProcrastinateShell,
    connector: testing.InMemoryConnector,
    capsys: pytest.CaptureFixture,
):
    await connector.defer_jobs_all(
        [
            t.JobToDefer(
                queue_name="queue1",
                task_name="task1",
                priority=0,
                lock="lock1",
                queueing_lock="queueing_lock1",
                args={},
                scheduled_at=conftest.aware_datetime(2000, 1, 1),
            ),
            t.JobToDefer(
                queue_name="queue2",
                task_name="task2",
                priority=0,
                lock="lock2",
                queueing_lock="queueing_lock2",
                args={},
                scheduled_at=conftest.aware_datetime(2000, 1, 1),
            ),
        ]
    )

    await utils.sync_to_async(
        shell.do_list_jobs, "id=2 queue=queue2 task=task2 lock=lock2 status=todo"
    )
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
                "worker_id": None,
            },
        )
    ]


async def test_list_jobs_details(
    shell: shell_module.ProcrastinateShell,
    connector: testing.InMemoryConnector,
    capsys: pytest.CaptureFixture,
):
    await connector.defer_jobs_all(
        [
            t.JobToDefer(
                queue_name="queue1",
                task_name="task1",
                priority=5,
                lock="lock1",
                queueing_lock="queueing_lock1",
                args={"x": 11},
                scheduled_at=conftest.aware_datetime(1000, 1, 1),
            ),
            t.JobToDefer(
                queue_name="queue2",
                task_name="task2",
                priority=7,
                lock="lock2",
                queueing_lock="queueing_lock2",
                args={"y": 22},
                scheduled_at=conftest.aware_datetime(2000, 1, 1),
            ),
        ]
    )

    await utils.sync_to_async(shell.do_list_jobs, "details")
    captured = capsys.readouterr()
    assert captured.out.splitlines() == [
        "#1 task1 on queue1 - [todo] (attempts=0, priority=5, scheduled_at=1000-01-01 "
        "00:00:00+00:00, args={'x': 11}, lock=lock1)",
        "#2 task2 on queue2 - [todo] (attempts=0, priority=7, scheduled_at=2000-01-01 "
        "00:00:00+00:00, args={'y': 22}, lock=lock2)",
    ]


async def test_list_jobs_empty(
    shell: shell_module.ProcrastinateShell,
    connector: testing.InMemoryConnector,
    capsys: pytest.CaptureFixture,
):
    await utils.sync_to_async(shell.do_list_jobs, "")
    captured = capsys.readouterr()
    assert captured.out == ""


async def test_list_queues(
    shell: shell_module.ProcrastinateShell,
    connector: testing.InMemoryConnector,
    capsys: pytest.CaptureFixture,
):
    await connector.defer_jobs_all(
        [
            t.JobToDefer(
                queue_name="queue1",
                task_name="task1",
                priority=0,
                lock="lock1",
                queueing_lock="queueing_lock1",
                args={},
                scheduled_at=conftest.aware_datetime(2000, 1, 1),
            ),
            t.JobToDefer(
                queue_name="queue2",
                task_name="task2",
                priority=0,
                lock="lock2",
                queueing_lock="queueing_lock2",
                args={},
                scheduled_at=conftest.aware_datetime(2000, 1, 1),
            ),
        ]
    )

    await utils.sync_to_async(shell.do_list_queues, "")
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


async def test_list_queues_filters(
    shell: shell_module.ProcrastinateShell,
    connector: testing.InMemoryConnector,
    capsys: pytest.CaptureFixture,
):
    await connector.defer_jobs_all(
        [
            t.JobToDefer(
                queue_name="queue1",
                task_name="task1",
                priority=0,
                lock="lock1",
                queueing_lock="queueing_lock1",
                args={},
                scheduled_at=conftest.aware_datetime(2000, 1, 1),
            ),
            t.JobToDefer(
                queue_name="queue2",
                task_name="task2",
                priority=0,
                lock="lock2",
                queueing_lock="queueing_lock2",
                args={},
                scheduled_at=conftest.aware_datetime(2000, 1, 1),
            ),
        ]
    )

    await utils.sync_to_async(
        shell.do_list_queues, "queue=queue2 task=task2 lock=lock2 status=todo"
    )
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


async def test_list_queues_empty(
    shell: shell_module.ProcrastinateShell,
    connector: testing.InMemoryConnector,
    capsys: pytest.CaptureFixture,
):
    await utils.sync_to_async(shell.do_list_queues, "")
    captured = capsys.readouterr()
    assert captured.out == ""


async def test_list_tasks(
    shell: shell_module.ProcrastinateShell,
    connector: testing.InMemoryConnector,
    capsys: pytest.CaptureFixture,
):
    await connector.defer_jobs_all(
        [
            t.JobToDefer(
                queue_name="queue1",
                task_name="task1",
                priority=0,
                lock="lock1",
                queueing_lock="queueing_lock1",
                args={},
                scheduled_at=conftest.aware_datetime(2000, 1, 1),
            ),
            t.JobToDefer(
                queue_name="queue2",
                task_name="task2",
                priority=0,
                lock="lock2",
                queueing_lock="queueing_lock2",
                args={},
                scheduled_at=conftest.aware_datetime(2000, 1, 1),
            ),
        ]
    )

    await utils.sync_to_async(shell.do_list_tasks, "")
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


async def test_list_tasks_filters(
    shell: shell_module.ProcrastinateShell,
    connector: testing.InMemoryConnector,
    capsys: pytest.CaptureFixture,
):
    await connector.defer_jobs_all(
        [
            t.JobToDefer(
                queue_name="queue1",
                task_name="task1",
                priority=0,
                lock="lock1",
                queueing_lock="queueing_lock1",
                args={},
                scheduled_at=conftest.aware_datetime(2000, 1, 1),
            ),
            t.JobToDefer(
                queue_name="queue2",
                task_name="task2",
                priority=0,
                lock="lock2",
                queueing_lock="queueing_lock2",
                args={},
                scheduled_at=conftest.aware_datetime(2000, 1, 1),
            ),
        ]
    )

    await utils.sync_to_async(
        shell.do_list_tasks, "queue=queue2 task=task2 lock=lock2 status=todo"
    )
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


async def test_list_tasks_empty(
    shell: shell_module.ProcrastinateShell,
    connector: testing.InMemoryConnector,
    capsys: pytest.CaptureFixture,
):
    await utils.sync_to_async(shell.do_list_tasks, "")
    captured = capsys.readouterr()
    assert captured.out == ""


async def test_list_locks(
    shell: shell_module.ProcrastinateShell,
    connector: testing.InMemoryConnector,
    capsys: pytest.CaptureFixture,
):
    await connector.defer_jobs_all(
        [
            t.JobToDefer(
                queue_name="queue1",
                task_name="task1",
                priority=0,
                lock="lock1",
                queueing_lock="queueing_lock1",
                args={},
                scheduled_at=conftest.aware_datetime(2000, 1, 1),
            ),
            t.JobToDefer(
                queue_name="queue2",
                task_name="task2",
                priority=0,
                lock="lock2",
                queueing_lock="queueing_lock2",
                args={},
                scheduled_at=conftest.aware_datetime(2000, 1, 1),
            ),
        ]
    )

    await utils.sync_to_async(shell.do_list_locks, "")
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


async def test_list_locks_filters(
    shell: shell_module.ProcrastinateShell,
    connector: testing.InMemoryConnector,
    capsys: pytest.CaptureFixture,
):
    await connector.defer_jobs_all(
        [
            t.JobToDefer(
                queue_name="queue1",
                task_name="task1",
                priority=0,
                lock="lock1",
                queueing_lock="queueing_lock1",
                args={},
                scheduled_at=conftest.aware_datetime(2000, 1, 1),
            ),
            t.JobToDefer(
                queue_name="queue2",
                task_name="task2",
                priority=0,
                lock="lock2",
                queueing_lock="queueing_lock2",
                args={},
                scheduled_at=conftest.aware_datetime(2000, 1, 1),
            ),
        ]
    )

    await utils.sync_to_async(
        shell.do_list_locks, "queue=queue2 task=task2 lock=lock2 status=todo"
    )
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


async def test_list_locks_empty(
    shell: shell_module.ProcrastinateShell,
    connector: testing.InMemoryConnector,
    capsys: pytest.CaptureFixture,
):
    await utils.sync_to_async(shell.do_list_locks, "")
    captured = capsys.readouterr()
    assert captured.out == ""


async def test_retry(
    shell: shell_module.ProcrastinateShell,
    connector: testing.InMemoryConnector,
    capsys: pytest.CaptureFixture,
):
    await connector.defer_jobs_all(
        [
            t.JobToDefer(
                queue_name="queue",
                task_name="task",
                priority=0,
                lock="lock",
                queueing_lock="queueing_lock",
                args={},
                scheduled_at=conftest.aware_datetime(2000, 1, 1),
            ),
        ]
    )
    await connector.set_job_status_run(1, "failed")

    await utils.sync_to_async(shell.do_list_jobs, "id=1")
    captured = capsys.readouterr()
    assert captured.out.strip() == "#1 task on queue - [failed]"

    await utils.sync_to_async(shell.do_retry, "1")
    captured = capsys.readouterr()
    assert captured.out.strip() == "#1 task on queue - [todo]"


async def test_cancel(
    shell: shell_module.ProcrastinateShell,
    connector: testing.InMemoryConnector,
    capsys: pytest.CaptureFixture,
):
    await connector.defer_jobs_all(
        [
            t.JobToDefer(
                queue_name="queue",
                task_name="task",
                priority=0,
                lock="lock",
                queueing_lock="queueing_lock",
                args={},
                scheduled_at=conftest.aware_datetime(2000, 1, 1),
            ),
        ]
    )

    await utils.sync_to_async(shell.do_list_jobs, "id=1")
    captured = capsys.readouterr()
    assert captured.out.strip() == "#1 task on queue - [todo]"

    await utils.sync_to_async(shell.do_cancel, "1")
    captured = capsys.readouterr()
    assert captured.out.strip() == "#1 task on queue - [cancelled]"
