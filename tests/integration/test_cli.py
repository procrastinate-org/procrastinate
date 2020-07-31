import pytest

from procrastinate import __version__, cli, jobs


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
    assert result.output.startswith("Usage:")


def test_version(entrypoint):
    result = entrypoint("--version")

    assert "procrastinate, version " + __version__ == result.output.strip()


def test_worker(entrypoint, click_app, mocker):
    click_app.run_worker = mocker.MagicMock()
    result = entrypoint(
        "--app yay worker --queues a,b --name=w1 --timeout=8.3 "
        "--one-shot --concurrency=10 --no-listen-notify"
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
    )


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


def test_healthchecks(entrypoint, click_app, mocker):
    check_db = mocker.patch(
        "procrastinate.healthchecks.HealthCheckRunner.check_connection"
    )
    check_db.return_value = True
    count_jobs = mocker.patch(
        "procrastinate.healthchecks.HealthCheckRunner.get_status_count"
    )
    count_jobs.return_value = {jobs.Status.SUCCEEDED: 42}

    result = entrypoint("-a yay healthchecks")

    assert result.output.startswith("DB connection: OK")
    check_db.assert_called_once_with()
    count_jobs.assert_called_once_with()


def test_healthchecks_bad_connection(entrypoint, click_app, mocker):
    check_db = mocker.patch(
        "procrastinate.healthchecks.HealthCheckRunner.check_connection"
    )
    check_db.return_value = False
    count_jobs = mocker.patch(
        "procrastinate.healthchecks.HealthCheckRunner.get_status_count"
    )

    result = entrypoint("-a yay healthchecks")

    assert result.output == "Cannot connect to DB\n"
    check_db.assert_called_once_with()
    count_jobs.assert_not_called()


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
    assert "there is already a job in the queue with the lock houba" in result.output
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
        "there is already a job in the queue with the lock houba (ignored)"
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
