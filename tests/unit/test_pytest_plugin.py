from __future__ import annotations

import importlib
import sys


def test_pytest_plugin_no_django(monkeypatch):
    monkeypatch.setitem(sys.modules, "procrastinate.contrib.django", None)
    monkeypatch.delitem(sys.modules, "procrastinate.pytest_plugin", raising=False)

    pytest_plugin = importlib.import_module("procrastinate.pytest_plugin")

    assert pytest_plugin.HAS_DJANGO is False
    assert not hasattr(pytest_plugin, "run_procrastinate_jobs")


def test_pytest_plugin_no_pytest(monkeypatch):
    monkeypatch.setitem(sys.modules, "pytest", None)
    monkeypatch.delitem(sys.modules, "procrastinate.pytest_plugin", raising=False)

    pytest_plugin = importlib.import_module("procrastinate.pytest_plugin")

    assert pytest_plugin.pytest is None
    assert not hasattr(pytest_plugin, "run_procrastinate_jobs")


def test_pytest_plugin_with_all_deps(monkeypatch):
    monkeypatch.delitem(sys.modules, "procrastinate.pytest_plugin", raising=False)

    pytest_plugin = importlib.import_module("procrastinate.pytest_plugin")

    assert pytest_plugin.HAS_DJANGO is True
    assert pytest_plugin.pytest is not None
    assert hasattr(pytest_plugin, "run_procrastinate_jobs")
