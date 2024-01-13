from __future__ import annotations

from procrastinate.contrib.django import utils


def test_connector_params():
    assert "dbname" in utils.connector_params()
