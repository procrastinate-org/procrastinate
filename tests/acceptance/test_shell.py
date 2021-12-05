import asyncio

import pytest

pytestmark = pytest.mark.asyncio


@pytest.fixture
async def shell(process_env):
    PIPE = asyncio.subprocess.PIPE
    proc = await asyncio.create_subprocess_exec(
        "procrastinate",
        "shell",
        env=process_env(),
        stdin=PIPE,
        stdout=PIPE,
        stderr=None,
    )
    yield proc
    proc.kill()
    await proc.wait()


@pytest.fixture
def write(shell):
    async def _(s: str):
        shell.stdin.write((s + "\n").encode())
        await shell.stdin.drain()

    return _


@pytest.fixture
def read(shell):
    async def _():
        # Read lines 1 by 1, concat them into a string that we return.
        # We accept to wait an indefinite amount of time at the beginning
        # but once we have started reading bytes, not reading anything
        lines = []
        prefix = "procrastinate>"

        while True:
            try:
                line = await asyncio.wait_for(shell.stdout.readline(), 0.1)
            except asyncio.TimeoutError:
                if lines:
                    break
                continue
            line = line.decode()
            if line.startswith(prefix):
                line = line[len(prefix) :]
            line = line.strip()
            if line:
                lines.append(line)
        return lines

    return _


async def test_shell(read, write, defer):
    assert await read() == [
        "Welcome to the procrastinate shell.   Type help or ? to list commands."
    ]
    defer("sum_task", ["--lock=a"], a=5, b=7)
    defer("sum_task", ["--lock=lock"], a=3, b=8)
    defer("sum_task", ["--queue=other", "--lock=lock"], a=1, b=2)
    defer("increment_task", ["--lock=b"], a=5)

    await write("cancel 2")
    assert await read() == ["#2 ns:tests.acceptance.app.sum_task on default - [failed]"]

    await write("cancel 3")
    assert await read() == ["#3 ns:tests.acceptance.app.sum_task on other - [failed]"]

    await write("cancel 4")
    assert await read() == [
        "#4 tests.acceptance.app.increment_task on default - [failed]"
    ]

    await write("list_jobs")
    assert await read() == [
        "#1 ns:tests.acceptance.app.sum_task on default - [todo]",
        "#2 ns:tests.acceptance.app.sum_task on default - [failed]",
        "#3 ns:tests.acceptance.app.sum_task on other - [failed]",
        "#4 tests.acceptance.app.increment_task on default - [failed]",
    ]

    await write("list_jobs queue=other details")
    assert await read() == [
        "#3 ns:tests.acceptance.app.sum_task on other - [failed] (attempts=0, scheduled_at=None, args={'a': 1, 'b': 2}, lock=lock)",
    ]

    await write("list_queues")
    assert await read() == [
        "default: 3 jobs (todo: 1, doing: 0, succeeded: 0, failed: 2)",
        "other: 1 jobs (todo: 0, doing: 0, succeeded: 0, failed: 1)",
    ]

    await write("list_tasks")
    assert await read() == [
        "ns:tests.acceptance.app.sum_task: 3 jobs (todo: 1, doing: 0, succeeded: 0, failed: 2)",
        "tests.acceptance.app.increment_task: 1 jobs (todo: 0, doing: 0, succeeded: 0, failed: 1)",
    ]

    await write("list_locks")
    assert await read() == [
        "a: 1 jobs (todo: 1, doing: 0, succeeded: 0, failed: 0)",
        "b: 1 jobs (todo: 0, doing: 0, succeeded: 0, failed: 1)",
        "lock: 2 jobs (todo: 0, doing: 0, succeeded: 0, failed: 2)",
    ]
