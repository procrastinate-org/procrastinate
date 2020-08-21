import pytest

from procrastinate import connector as connector_module
from procrastinate import exceptions


def test_open(connector):
    connector.open()


@pytest.mark.asyncio
async def test_open_async(connector):
    await connector.open_async()


def test_close(connector):
    connector.close()


@pytest.mark.asyncio
async def test_close_async(connector):
    await connector.close_async()


@pytest.mark.parametrize(
    "method_name, kwargs",
    [
        ["open_async", {}],
        ["close_async", {}],
        ["execute_query_async", {"query": ""}],
        ["execute_query_one_async", {"query": ""}],
        ["execute_query_all_async", {"query": ""}],
        ["listen_notify", {"event": None, "channels": []}],
    ],
)
@pytest.mark.asyncio
async def test_missing_app_async(method_name, kwargs):
    with pytest.raises(exceptions.SyncConnectorConfigurationError):
        # Some of this methods are not async but they'll raise
        # before the await is reached.
        await getattr(connector_module.BaseConnector(), method_name)(**kwargs)
