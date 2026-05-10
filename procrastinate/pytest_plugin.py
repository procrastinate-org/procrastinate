"""
This module provides a Pytest plugin for Procrastinate, automatically registered
via entry points if pytest is installed.

It exists to provide convenient fixtures for running background jobs directly
within a test suite, avoiding the boilerplate required to manually set up a
worker and configure the `DjangoTestingConnector`.

The plugin ensures a smooth developer experience for Procrastinate users who
rely on pytest to test their applications, particularly those utilizing the
Django integration.
"""

from __future__ import annotations

import typing
from collections.abc import Awaitable

try:
    import pytest
except ImportError:
    pytest = None  # type: ignore

HAS_DJANGO = False
try:
    from procrastinate.contrib.django import app as django_app
    from procrastinate.contrib.django import testing

    HAS_DJANGO = True  # pyright: ignore[reportConstantRedefinition]
except ImportError:
    pass


if pytest and HAS_DJANGO:

    @pytest.fixture
    def run_procrastinate_jobs() -> typing.Callable[..., None]:
        """
        Fixture that provides a synchronous function to execute all awaiting Procrastinate jobs.

        In an integration test environment, you often defer jobs that need to be processed
        before asserting the outcome. This fixture simplifies that process by injecting the
        `DjangoTestingConnector` into the current app and running the worker.

        It exists so developers can predictably execute jobs inline during their tests,
        without spawning separate processes or managing background workers.
        """

        def f(**kwargs: typing.Any) -> None:
            kwargs.setdefault("wait", False)
            kwargs.setdefault("install_signal_handlers", False)
            kwargs.setdefault("listen_notify", False)
            with django_app.replace_connector(testing.DjangoTestingConnector()):  # pyright: ignore[reportPossiblyUnboundVariable]
                django_app.run_worker(**kwargs)  # pyright: ignore[reportPossiblyUnboundVariable]

        return f

    @pytest.fixture
    def arun_procrastinate_jobs() -> typing.Callable[..., Awaitable[None]]:
        """
        Fixture that provides an asynchronous function to execute all awaiting Procrastinate jobs.

        Similar to `run_procrastinate_jobs`, but designed for use within `pytest.mark.asyncio`
        tests. It allows developers to await the processing of background jobs within their
        async test suites, replacing the app's connector with the `DjangoTestingConnector`
        for the duration of the execution.
        """

        async def f(**kwargs: typing.Any) -> None:
            kwargs.setdefault("wait", False)
            kwargs.setdefault("install_signal_handlers", False)
            kwargs.setdefault("listen_notify", False)
            with django_app.replace_connector(testing.DjangoTestingConnector()):  # pyright: ignore[reportPossiblyUnboundVariable]
                await django_app.run_worker_async(**kwargs)  # pyright: ignore[reportPossiblyUnboundVariable]

        return f
