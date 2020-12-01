import pytest

from procrastinate import __version__, cli, exceptions


@pytest.fixture
def entrypoint(cli_runner):
    def ep(args=""):
        return cli_runner.invoke(cli.cli, args.split(), catch_exceptions=False)

    return ep


@pytest.fixture
def click_app(mocker, app):
    mocker.patch("procrastinate.App.from_path", return_value=app)
    yield app


def test_cli(entrypoint):
    result = entrypoint()
    print(result.output)
    assert result.output.startswith("Usage:")


def test_version(entrypoint):
    result = entrypoint("--version")

    assert "procrastinate, version " + __version__ == result.output.strip()


def test_worker(entrypoint, click_app, mocker):
    click_app.run_worker = mocker.MagicMock()
    log = mocker.patch("procrastinate.cli.configure_logging")
    result = entrypoint(
        "--app yay "
        "-vvv --log-format={message},yay! --log-format-style={ "
        "worker "
        " --queues a,b --name=w1 --timeout=8.3 "
        "--one-shot --concurrency=10 --no-listen-notify --delete-jobs=always"
    )

    assert result.output.strip() == "Launching a worker on a, b"
    assert result.exit_code == 0
    click_app.run_worker.assert_called_once_with(
        concurrency=10,
        name="w1",
        queues=["a", "b"],
        timeout=8.3,
        wait=False,
        listen_notify=False,
        delete_jobs="always",
    )
    log.assert_called_once_with(verbosity=3, format="{message},yay!", style="{")


def test_schema_apply(entrypoint, click_app, mocker):
    apply_schema = mocker.patch("procrastinate.schema.SchemaManager.apply_schema")
    result = entrypoint("-a yay schema --apply")

    assert result.output.strip() == "Applying schema\nDone"
    assert result.exit_code == 0
    apply_schema.assert_called_once_with()


def test_schema_read(entrypoint):
    result = entrypoint("schema --read")

    assert result.output.startswith("-- Procrastinate Schema")
    assert result.exit_code == 0


def test_schema_migrations_path(entrypoint):
    result = entrypoint("schema --migrations-path")

    assert result.output.endswith("sql/migrations\n")
    assert result.exit_code == 0


def test_healthchecks(entrypoint, click_app):
    result = entrypoint("-a yay healthchecks")

    assert result.output.startswith("App configuration: OK")


def test_healthchecks_no_schema(entrypoint, click_app, connector):
    connector.table_exists = False

    result = entrypoint("-a yay healthchecks")

    assert "procrastinate_jobs table was not found" in result.output


def test_healthchecks_bad_connection(entrypoint, click_app, mocker):
    mocker.patch.object(
        click_app.job_manager,
        "check_connection",
        side_effect=exceptions.ConnectorException("Something's wrong"),
    )

    result = entrypoint("-a yay healthchecks")

    assert result.output.strip() == "Error: Something's wrong"


def test_no_app(entrypoint, mocker):
    result = entrypoint("schema --apply")
    assert result.exit_code != 0
    assert "Missing app" in result.output


def test_defer(entrypoint, click_app, connector):
    @click_app.task(name="hello")
    def mytask(a):
        pass

    # No space in the json helps entrypoint() to simply split args
    result = entrypoint(
        """-a yay defer --lock=sherlock --queueing-lock=houba hello {"a":1}"""
    )

    assert result.output == "Launching a job: hello(a=1)\n"
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
        }
    }


def test_defer_queueing_lock(entrypoint, click_app, connector):
    @click_app.task(name="hello")
    def mytask(a):
        pass

    click_app.configure_task(name="hello", queueing_lock="houba").defer(a=1)

    result = entrypoint("""-a yay defer --queueing-lock=houba hello {"a":2}""")

    assert result.exit_code > 0
    assert (
        "there is already a job in the queue with the queueing lock houba"
        in result.output
    )
    assert len(connector.jobs) == 1


def test_defer_queueing_lock_ignore(entrypoint, click_app, connector):
    @click_app.task(name="hello")
    def mytask(a):
        pass

    click_app.configure_task(name="hello", queueing_lock="houba").defer(a=1)

    result = entrypoint(
        """-a yay defer --queueing-lock=houba --ignore-already-enqueued hello {"a":2}"""
    )

    assert result.exit_code == 0
    assert (
        "there is already a job in the queue with the queueing lock houba (ignored)"
        in result.output
    )
    assert len(connector.jobs) == 1


def test_defer_unknown(entrypoint, click_app, connector):
    # No space in the json helps entrypoint() to simply split args
    result = entrypoint(
        """-a yay defer --unknown --lock=sherlock --queueing-lock=houba hello {"a":1}"""
    )

    assert result.output == "Launching a job: hello(a=1)\n"
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
        }
    }


@pytest.mark.parametrize(
    "input",
    [
        # Unparsable at
        "defer --at=yay mytask",
        # Define both in and at
        "defer --in=3 --at=2000-01-01T00:00:00Z mytask",
        # Invalid Json
        "defer hello {",
        # Unknown task
        "defer hello",
    ],
)
def test_defer_error(entrypoint, input):
    result = entrypoint(input)
    assert result.exit_code != 0


def test_shell(entrypoint, click_app, mocker):
    shell = mocker.patch("procrastinate.shell.ProcrastinateShell")

    result = entrypoint("shell")
    shell.return_value.cmdloop.assert_called_once_with()
    assert result.exit_code == 0
