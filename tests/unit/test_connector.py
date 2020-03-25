import pytest


def test_close(connector):
    connector.close()


@pytest.mark.asyncio
async def test_close_async(connector):
    await connector.close_async()
