from unittest.mock import MagicMock

import pytest

from procrastinate import aiopg_connector, psycopg2_connector


class AsyncMock(MagicMock):
    async def __call__(self, *args, **kwargs):
        return super(AsyncMock, self).__call__(*args, **kwargs)


@pytest.fixture
def mock_connector_open(app, mocker):
    return mocker.patch.object(app.connector, "open")


@pytest.fixture
def mock_connector_close(app, mocker):
    return mocker.patch.object(app.connector, "close")


@pytest.fixture
def mock_connector_open_async(app, mocker):
    return mocker.patch.object(
        app.connector, "open_async", new_callable=AsyncMock
    )


@pytest.fixture
def mock_connector_close_async(app, mocker):
    return mocker.patch.object(
        app.connector, "close_async", new_callable=AsyncMock
    )


@pytest.fixture
def pool():
    return MagicMock()


@pytest.fixture
def mock_async_create_pool(mocker):
    return mocker.patch.object(
        aiopg_connector.AiopgConnector, "_create_pool", new_callable=AsyncMock
    )


@pytest.fixture
def mock_create_pool(mocker):
    return mocker.patch.object(psycopg2_connector.Psycopg2Connector, "_create_pool")
