from unittest.mock import MagicMock

import pytest

from procrastinate import aiopg_connector, psycopg2_connector


class AsyncMock(MagicMock):
    async def __call__(self, *args, **kwargs):
        return super(AsyncMock, self).__call__(*args, **kwargs)


@pytest.fixture
def pool():
    return MagicMock()


