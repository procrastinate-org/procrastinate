from __future__ import annotations

import asyncio
from collections.abc import Awaitable
from typing import TypeVar

import pytest

T = TypeVar("T")


async def wait_or_fail(
    awaitable: Awaitable[T], timeout: float = 2, reason: str | None = None
) -> T:
    """
    Wait for `awaitable` and return its result, failing the test if it isn't done
    within `timeout`.

    Unlike asyncio.wait_for, this doesn't cancel it on timeout: a cancelled worker
    waits for its shutdown without any deadline, so a stuck worker would hang the
    test instead of failing it.
    """
    task = asyncio.ensure_future(awaitable)
    done, _ = await asyncio.wait({task}, timeout=timeout)
    if not done:
        pytest.fail(reason or f"Not done within {timeout}s: {task!r}")
    return task.result()
