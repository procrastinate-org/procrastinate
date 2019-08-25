import logging

import click
import pytest

from procrastinate import cli, exceptions


@pytest.mark.parametrize(
    "verbosity, log_level", [(0, "INFO"), (1, "DEBUG"), (2, "DEBUG")]
)
def test_get_log_level(verbosity, log_level):
    assert cli.get_log_level(verbosity=verbosity) == getattr(logging, log_level)


def test_set_verbosity(mocker, caplog):
    config = mocker.patch("logging.basicConfig")

    caplog.set_level("DEBUG")

    cli.set_verbosity(1)

    config.assert_called_once_with(level=logging.DEBUG)
    records = [record for record in caplog.records if record.action == "set_log_level"]
    assert len(records) == 1
    assert records[0].value == "DEBUG"


@pytest.mark.parametrize(
    "raised, expected",
    [
        # Procrastinate exceptions are caught
        (exceptions.ProcrastinateException, click.ClickException),
        # Other exceptions are not
        (ValueError, ValueError),
    ],
)
def test_handle_errors(raised, expected):
    @cli.handle_errors()
    def raise_exc():
        raise exceptions.ProcrastinateException

    with pytest.raises(click.ClickException):
        raise_exc()


def test_handle_errors_no_error():
    @cli.handle_errors()
    def raise_exc():
        assert True

    raise_exc()


def test_main(mocker):

    environ = mocker.patch("os.environ", {"LANG": "fr-FR.UTF-8"})
    mocker.patch("procrastinate.cli.cli")
    cli.main()

    assert environ == {"LANG": "fr-FR.UTF-8", "LC_ALL": "C.UTF-8"}
