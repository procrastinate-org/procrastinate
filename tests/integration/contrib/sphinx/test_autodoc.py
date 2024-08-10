from __future__ import annotations

import pytest


@pytest.mark.sphinx(buildername="html", testroot="root")
def test_autodoc_task(sphinx_app):
    sphinx_app.build()
    content = (sphinx_app.outdir / "index.html").read_text()
    # Check that the docstring of one of the task appears in the generated documentation
    assert "Sum two numbers." in content
