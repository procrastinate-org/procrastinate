from __future__ import annotations

import pytest

from procrastinate.contrib.django import utils


def test_connector_params():
    params, pool_params = utils.connector_params()
    assert "dbname" in params
    assert pool_params == {"min_size": 1, "max_size": 4}


@pytest.mark.parametrize(
    "package_name, expected",
    [
        ("foo" * 30, False),
        ("pytest", True),
    ],
)
def test_package_is_installed(package_name, expected):
    assert utils.package_is_installed(package_name) is expected


@pytest.mark.parametrize(
    "version, version_wanted,expected",
    [
        ("3.1.3", 3, True),
        ("2.1.3", 3, False),
        ("pytest", 3, False),
        (None, 3, False),
    ],
)
def test_package_is_version(version, version_wanted, expected, mocker):
    mocker.patch("importlib.metadata.version", return_value=version)

    assert utils.package_is_version("abcd", version_wanted) is expected
