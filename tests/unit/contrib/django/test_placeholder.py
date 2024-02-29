from __future__ import annotations

import pytest

from procrastinate import app, blueprints
from procrastinate.contrib.django import exceptions, placeholder


def test__not_ready():
    message = (
        r"Cannot call procrastinate.contrib.app.foo\(\) before the "
        r"'procrastinate.contrib.django' django app is ready\."
    )
    with pytest.raises(
        exceptions.DjangoNotReady,
        match=message,
    ):
        placeholder._not_ready("foo")


def test_FutureApp__not_ready():
    with pytest.raises(exceptions.DjangoNotReady):
        placeholder.FutureApp().open()


def test_FutureApp__defer():
    app = placeholder.FutureApp()

    @app.task
    def foo():
        pass

    with pytest.raises(exceptions.DjangoNotReady):
        foo.defer()


def test_FutureApp__shadowed_methods():
    ignored = {"from_path"}
    added = {"will_configure_task"}
    app_methods = set(dir(app.App)) - set(dir(blueprints.Blueprint)) - ignored | added
    assert sorted(placeholder.FutureApp._shadowed_methods) == sorted(app_methods)
