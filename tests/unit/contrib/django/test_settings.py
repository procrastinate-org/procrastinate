from __future__ import annotations

from procrastinate.contrib.django import settings as procrastinate_settings


def test_BaseSettings(settings):
    settings.PROCRASTINATE_FOO = "bar"

    class MySettings(procrastinate_settings.BaseSettings):
        FOO: str = "baz"

    assert MySettings().FOO == "bar"


def test_BaseSettings__default():
    class MySettings(procrastinate_settings.BaseSettings):
        FOO: str = "baz"

    assert MySettings().FOO == "baz"
