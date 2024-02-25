from __future__ import annotations

import pytest

from procrastinate.contrib.django import utils


def test_connector_params():
    assert "dbname" in utils.connector_params()


def test_get_settings(settings):
    settings.PROCRASTINATE_FOO = "bar"
    assert utils.get_setting("FOO", default="baz") == "bar"


def test_get_settings_default():
    assert utils.get_setting("FOO", default="baz") == "baz"


@pytest.mark.parametrize(
    "package_name, expected",
    [
        ("foo" * 30, False),
        ("pytest", True),
    ],
)
def test_package_is_installed(package_name, expected):
    assert utils.package_is_installed(package_name) is expected
