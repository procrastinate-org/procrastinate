from unittest.mock import MagicMock

import pytest


class AsyncMock(MagicMock):
    """Provides a Mock object that can be awaited.

    Unfortunately AsyncMock does not natively exists before python3.8.
    """

    def __init__(self):
        super().__init__()
        self.was_awaited = False

    def __await__(self):
        self.was_awaited = True
        return iter([])


@pytest.fixture
def pool():
    return MagicMock()


@pytest.fixture
def engine():
    return MagicMock()
