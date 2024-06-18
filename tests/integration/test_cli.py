from __future__ import annotations

import asyncio
import dataclasses
import datetime
import logging
import os

import pytest

from procrastinate import __version__, cli, exceptions, worker


@dataclasses.dataclass
class CallResult:
    exit_code: int
    stdout: str
    stderr: str


@pytest.fixture
async def entrypoint(capsys, monkeypatch):
    async def ep(args=""):
        # basicConfig works better if handlers config is properly isolated
        logging.getLogger("").handlers = []
        # This will create an event loop. Let's ensure we're not already in one.
        asyncio.set_event_loop(None)
        exit_code = 0
        try:
            await cli.cli(args.split())
        except SystemExit as exc:
            exit_code = exc.code if isinstance(exc.code, int) else 1
        captured = capsys.readouterr()
        return CallResult(exit_code=exit_code, stdout=captured.out, stderr=captured.err)

    monkeypatch.setenv("PROCRASTINATE_VERBOSE", "0")
    logging.getLogger("").handlers = []
    return ep


@pytest.fixture
def cli_app(mocker, app):
    os.environ["PROCRASTINATE_APP"] = "foo"
    mocker.patch("procrastinate.App.from_path", return_value=app)
    yield app
    del os.environ["PROCRASTINATE_APP"]


async def test_cli(entrypoint):
    result = await entrypoint()
    print(result)
    assert result.stderr.startswith("usage:")


async def test_cli_logging_configuration(entrypoint, cli_app):
    result = await entrypoint(
        "--verbose --log-format {message},yay! --log-format-style { healthchecks"
    )
    assert "Log level set to DEBUG,yay!" in result.stderr


async def test_version(entrypoint):
    result = await entrypoint("--version")

    assert "procrastinate, version " + __version__ == result.stdout.strip()


async def test_worker(entrypoint, cli_app, mocker):
    cli_app.run_worker_async = mocker.AsyncMock()
    result = await entrypoint(
        "worker "
        "--queues a,b --name=w1 --timeout=8.3 "
        "--one-shot --concurrency=10 --no-listen-notify --delete-jobs=always"
    )

    assert "Launching a worker on a, b" in result.stderr.strip()
    assert result.exit_code == 0
    cli_app.run_worker_async.assert_called_once_with(
        concurrency=10,
        name="w1",
        queues=["a", "b"],
        timeout=8.3,
        wait=False,
        listen_notify=False,
        delete_jobs=worker.DeleteJobCondition.ALWAYS,
    )


async def test_schema_apply(entrypoint, cli_app, mocker):
    apply_schema_async = mocker.patch(
        "procrastinate.schema.SchemaManager.apply_schema_async"
    )
    result = await entrypoint("schema --apply")

    assert result.stderr.strip() == "Applying schema\nDone"
    assert result.exit_code == 0
    apply_schema_async.assert_called_once_with()


async def test_schema_read(entrypoint):
    result = await entrypoint("schema --read")

    assert result.stdout.startswith("-- Procrastinate Schema")
    assert result.exit_code == 0


async def test_schema_migrations_path(entrypoint):
    result = await entrypoint("schema --migrations-path")

    assert result.stdout.endswith("sql/migrations\n")
    assert result.exit_code == 0


async def test_healthchecks(entrypoint, cli_app):
    result = await entrypoint("healthchecks")

    assert result.stdout.startswith("App configuration: OK")


async def test_healthchecks_no_schema(entrypoint, cli_app, connector):
    connector.table_exists = False

    result = await entrypoint("healthchecks")

    assert "procrastinate_jobs table was not found" in result.stderr


async def test_healthchecks_bad_connection(entrypoint, cli_app, mocker):
    mocker.patch.object(
        cli_app.job_manager,
        "check_connection_async",
        side_effect=exceptions.ConnectorException("Something's wrong"),
    )

    result = await entrypoint("healthchecks")

    assert "Something's wrong" in result.stderr


async def test_no_app(entrypoint, mocker):
    result = await entrypoint("schema --apply")
    assert result.exit_code != 0
    assert "Missing app" in result.stderr


async def test_defer(entrypoint, cli_app, connector):
    @cli_app.task(name="hello")
    def mytask(a):
        pass

    # No space in the json helps entrypoint() to simply split args
    result = await entrypoint(
        """defer --lock=sherlock --queueing-lock=houba hello {"a":1}"""
    )

    assert "Launching a job: hello(a=1)\n" in result.stderr
    assert result.exit_code == 0
    assert connector.jobs == {
        1: {
            "args": {"a": 1},
            "attempts": 0,
            "id": 1,
            "lock": "sherlock",
            "queueing_lock": "houba",
            "queue_name": "default",
            "scheduled_at": None,
            "status": "todo",
            "task_name": "hello",
            "priority": 0,
        }
    }


async def test_defer_priority(entrypoint, cli_app, connector):
    @cli_app.task(name="hello")
    def mytask(a):
        pass

    result = await entrypoint("""defer --lock=sherlock --priority=5 hello {"a":1}""")

    assert "Launching a job: hello(a=1)\n" in result.stderr
    assert result.exit_code == 0
    assert connector.jobs == {
        1: {
            "args": {"a": 1},
            "attempts": 0,
            "id": 1,
            "lock": "sherlock",
            "queueing_lock": None,
            "queue_name": "default",
            "scheduled_at": None,
            "status": "todo",
            "task_name": "hello",
            "priority": 5,
        }
    }


async def test_defer_at(entrypoint, cli_app, connector):
    @cli_app.task(name="hello")
    def mytask(a):
        pass

    # No space in the json helps entrypoint() to simply split args
    result = await entrypoint(
        """defer --lock=sherlock --at=2020-01-01T12:00:00Z hello {"a":1}"""
    )

    assert "Launching a job: hello(a=1)\n" in result.stderr
    assert result.exit_code == 0
    assert connector.jobs == {
        1: {
            "args": {"a": 1},
            "attempts": 0,
            "id": 1,
            "lock": "sherlock",
            "queueing_lock": None,
            "queue_name": "default",
            "scheduled_at": datetime.datetime(
                2020, 1, 1, 12, tzinfo=datetime.timezone.utc
            ),
            "status": "todo",
            "task_name": "hello",
            "priority": 0,
        }
    }


async def test_defer_in(entrypoint, cli_app, connector):
    @cli_app.task(name="hello")
    def mytask(a):
        pass

    now = datetime.datetime.now(datetime.timezone.utc)

    # No space in the json helps entrypoint() to simply split args
    result = await entrypoint("""defer --lock=sherlock --in=10 hello {"a":1}""")

    assert "Launching a job: hello(a=1)\n" in result.stderr
    assert result.exit_code == 0
    assert len(connector.jobs) == 1
    job = connector.jobs[1]
    scheduled_at = job.pop("scheduled_at")
    assert job == {
        "args": {"a": 1},
        "attempts": 0,
        "id": 1,
        "lock": "sherlock",
        "queueing_lock": None,
        "queue_name": "default",
        "status": "todo",
        "task_name": "hello",
        "priority": 0,
    }
    assert (
        now + datetime.timedelta(seconds=9)
        < scheduled_at
        < now + datetime.timedelta(seconds=11)
    )


async def test_defer_queueing_lock(entrypoint, cli_app, connector):
    @cli_app.task(name="hello")
    def mytask(a):
        pass

    await cli_app.configure_task(name="hello", queueing_lock="houba").defer_async(a=1)

    result = await entrypoint("""defer --queueing-lock=houba hello {"a":2}""")

    assert result.exit_code > 0
    assert (
        "there is already a job in the queue with the queueing lock houba"
        in result.stderr
    )
    assert len(connector.jobs) == 1


async def test_defer_queueing_lock_ignore(entrypoint, cli_app, connector):
    @cli_app.task(name="hello")
    def mytask(a):
        pass

    cli_app.configure_task(name="hello", queueing_lock="houba").defer(a=1)

    result = await entrypoint(
        """defer --queueing-lock=houba --ignore-already-enqueued hello {"a":2}"""
    )

    assert result.exit_code == 0
    assert (
        "there is already a job in the queue with the queueing lock houba (ignored)"
        in result.stderr
    )
    assert len(connector.jobs) == 1


async def test_defer_unknown(entrypoint, cli_app, connector):
    # No space in the json helps entrypoint() to simply split args
    result = await entrypoint(
        """defer --unknown --lock=sherlock --queueing-lock=houba hello {"a":1}"""
    )

    assert "Launching a job: hello(a=1)" in result.stderr
    assert result.exit_code == 0
    assert connector.jobs == {
        1: {
            "args": {"a": 1},
            "attempts": 0,
            "id": 1,
            "lock": "sherlock",
            "queueing_lock": "houba",
            "queue_name": "default",
            "scheduled_at": None,
            "status": "todo",
            "task_name": "hello",
            "priority": 0,
        }
    }


@pytest.mark.parametrize(
    "input",
    [
        # Invalid Json
        "defer hello {",
        # Unknown task
        "defer hello",
    ],
)
async def test_defer_error(entrypoint, input):
    result = await entrypoint(input)
    assert result.exit_code != 0


async def test_shell(entrypoint, cli_app, mocker):
    shell = mocker.patch("procrastinate.shell.ProcrastinateShell")

    result = await entrypoint("shell")
    assert result.exit_code == 0, result.stderr
    shell.return_value.cmdloop.assert_called_once_with()
