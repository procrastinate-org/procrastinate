from __future__ import annotations

import pytest
from django.core.management import call_command


def test_procrastinate_command(capsys):
    with pytest.raises(SystemExit):
        call_command("procrastinate", "--help")

    out, err = capsys.readouterr()
    assert "usage:  procrastinate" in out
    assert "{worker,defer,shell}" in out
