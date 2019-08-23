import pytest

from procrastinate import __version__, cli


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

    assert "procrastinate " + __version__ in result.output
    assert "License: MIT License" in result.output


def test_worker(entrypoint, click_app, mocker):
    click_app.run_worker = mocker.MagicMock()
    result = entrypoint("-a yay worker a b")

    assert result.output.strip() == "Launching a worker on a, b"
    assert result.exit_code == 0
    click_app.run_worker.assert_called_once_with(queues=["a", "b"])


def test_migrate(entrypoint, click_app, mocker):
    migrate = mocker.patch("procrastinate.migration.Migrator.migrate")
    result = entrypoint("-a yay migrate")

    assert result.output.strip() == "Launching migrations\nDone"
    assert result.exit_code == 0
    migrate.assert_called_once_with()


def test_migrate_text(entrypoint):
    result = entrypoint("migrate --text")

    assert result.output.startswith("CREATE")
    assert result.exit_code == 0


def test_no_app(entrypoint, mocker):
    click_app.run_worker = mocker.MagicMock()
    with pytest.raises(NotImplementedError):
        entrypoint("migrate")
