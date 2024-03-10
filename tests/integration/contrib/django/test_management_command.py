from __future__ import annotations

import pytest
from django.core import exceptions as django_exceptions
from django.core.management import call_command
from django.db import utils as db_utils


def test_procrastinate_command(capsys):
    with pytest.raises(SystemExit):
        call_command("procrastinate", "--help")

    out, err = capsys.readouterr()
    assert "usage:  procrastinate" in out
    assert "{worker,defer,healthchecks,shell}" in out


def test_procrastinate_command__healthchecks(db, capsys):
    call_command("procrastinate", "healthchecks")

    out, _ = capsys.readouterr()
    expected = """Database connection: OK
Migrations: OK
Default Django Procrastinate App: OK
Worker App: OK"""
    assert out.strip() == expected


def test_procrastinate_command__healthchecks__connection_failure(db, mocker, capsys):
    connection = mocker.Mock()
    connection.ensure_connection.side_effect = db_utils.DatabaseError("boom")
    mocker.patch(
        "procrastinate.contrib.django.healthchecks.connections",
        {"default": connection},
    )

    with pytest.raises(SystemExit):
        call_command("procrastinate", "healthchecks")

    _, err = capsys.readouterr()
    assert "boom" in err


def test_procrastinate_command__healthchecks__migrations_executor_failure(
    db, mocker, capsys
):
    connection = mocker.Mock()
    connection.ensure_connection.side_effect = Exception("boom")
    mocker.patch(
        "django.db.migrations.executor.MigrationExecutor",
        side_effect=django_exceptions.ImproperlyConfigured("boom"),
    )

    with pytest.raises(SystemExit):
        call_command("procrastinate", "healthchecks")

    _, err = capsys.readouterr()
    assert "boom" in err


def test_procrastinate_command__healthchecks__missing_migrations(db, mocker, capsys):
    connection = mocker.Mock()
    connection.ensure_connection.side_effect = Exception("boom")
    executor = mocker.patch(
        "django.db.migrations.executor.MigrationExecutor",
    )
    executor.return_value.migration_plan.return_value = [
        (mocker.Mock(app_label="procrastinate"), None)
    ]

    with pytest.raises(SystemExit):
        call_command("procrastinate", "healthchecks")

    _, err = capsys.readouterr()
    assert "Missing procrastinate migrations" in err
