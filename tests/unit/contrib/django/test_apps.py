from __future__ import annotations

from procrastinate import blueprints
from procrastinate.contrib.django import apps


def test_get_settings(settings):
    settings.PROCRASTINATE_FOO = "bar"
    assert apps.get_setting("FOO", default="baz") == "bar"


def test_get_settings_default():
    assert apps.get_setting("FOO", default="baz") == "baz"


def test_get_import_paths__no_autodiscover(settings):
    settings.PROCRASTINATE_AUTODISCOVER_MODULE_NAME = None
    settings.PROCRASTINATE_IMPORT_PATHS = ["foo", "bar"]
    assert list(apps.get_import_paths()) == ["foo", "bar"]


def test_get_import_paths(settings, mocker):
    settings.PROCRASTINATE_AUTODISCOVER_MODULE_NAME = "yay"
    am = mocker.patch("django.utils.module_loading.autodiscover_modules")

    assert list(apps.get_import_paths()) == []
    am.assert_called_once_with("yay")


def test_create_app():
    bp = blueprints.Blueprint()

    @bp.task(name="foo")
    def foo():
        pass

    app = apps.create_app(blueprint=bp)
    assert "foo" in app.tasks


def test_create_app__no_task():
    apps.create_app(blueprint=blueprints.Blueprint())
