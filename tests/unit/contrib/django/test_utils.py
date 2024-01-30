from __future__ import annotations

from procrastinate.contrib.django import utils


def test_connector_params():
    assert "dbname" in utils.connector_params()


def test_get_settings(settings):
    settings.PROCRASTINATE_FOO = "bar"
    assert utils.get_setting("FOO", default="baz") == "bar"


def test_get_settings_default():
    assert utils.get_setting("FOO", default="baz") == "baz"
