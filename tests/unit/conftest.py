from unittest.mock import MagicMock

import pytest


class AsyncMock(MagicMock):
    """Provides a Mock object that can be awaited.

    Unfortunately AsyncMock does not natively exists before python3.7.
    """

    def __init__(self):
        super(AsyncMock, self).__init__()
        self.was_awaited = False

    def __await__(self):
        self.was_awaited = True
        return iter([])


@pytest.fixture
def pool():
    return MagicMock()
