from __future__ import annotations

import pytest

from procrastinate import app, blueprints
from procrastinate.contrib.django import exceptions, procrastinate_app


def test__not_ready():
    message = (
        r"Cannot call procrastinate.contrib.app.foo\(\) before the "
        r"'procrastinate.contrib.django' django app is ready\."
    )
    with pytest.raises(
        exceptions.DjangoNotReady,
        match=message,
    ):
        procrastinate_app._not_ready("foo")


def test_FutureApp__not_ready():
    with pytest.raises(exceptions.DjangoNotReady):
        procrastinate_app.FutureApp().open()


def test_FutureApp__defer():
    app = procrastinate_app.FutureApp()

    @app.task
    def foo():
        pass

    with pytest.raises(exceptions.DjangoNotReady):
        foo.defer()


def test_FutureApp__shadowed_methods():
    ignored = {"from_path"}
    added = {"will_configure_task"}
    app_methods = set(dir(app.App)) - set(dir(blueprints.Blueprint)) - ignored | added
    assert sorted(procrastinate_app.FutureApp._shadowed_methods) == sorted(app_methods)
