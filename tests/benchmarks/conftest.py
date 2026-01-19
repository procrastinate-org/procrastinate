from __future__ import annotations

import asyncio
import inspect

import pytest


@pytest.fixture
def aio_benchmark(benchmark):
    def _wrapper(func, *args, **kwargs):
        if inspect.iscoroutinefunction(func):
            event_loop = asyncio.get_event_loop()

            @benchmark
            def _():
                return event_loop.run_until_complete(func(*args, **kwargs))
        else:
            benchmark(func, *args, **kwargs)

    return _wrapper
