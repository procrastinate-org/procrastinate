from __future__ import annotations

import pytest
from sphinx.testing.path import path

pytest_plugins = ["sphinx.testing.fixtures"]


@pytest.fixture(scope="session")
def rootdir():
    return path(__file__).parent


@pytest.fixture
def sphinx_app(app_params, make_app):
    """
    Provides the 'sphinx.application.Sphinx' object
    """
    args, kwargs = app_params
    return make_app(*args, **kwargs)
