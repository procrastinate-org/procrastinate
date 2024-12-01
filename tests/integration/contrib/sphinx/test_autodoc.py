from __future__ import annotations

import pathlib

import pytest


@pytest.fixture
def rootdir():
    return pathlib.Path(__file__).parent


@pytest.fixture
def sphinx_app(app_params, make_app):
    """
    Provides the 'sphinx.application.Sphinx' object
    """
    args, kwargs = app_params
    return make_app(*args, **kwargs)


@pytest.mark.sphinx(buildername="html", testroot="root")
def test_autodoc_task(sphinx_app):
    sphinx_app.build()
    content = (sphinx_app.outdir / "index.html").read_text()
    # Check that the docstring of one of the task appears in the generated documentation
    assert "Sum two numbers." in content
