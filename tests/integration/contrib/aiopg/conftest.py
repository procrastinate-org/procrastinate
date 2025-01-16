from __future__ import annotations

import pytest

from procrastinate.contrib.aiopg import aiopg_connector as aiopg


@pytest.fixture
async def aiopg_connector_factory(connection_params):
    connectors = []

    async def _(*, open: bool = True, **kwargs):
        json_dumps = kwargs.pop("json_dumps", None)
        json_loads = kwargs.pop("json_loads", None)
        connection_params.update(kwargs)
        connector = aiopg.AiopgConnector(
            json_dumps=json_dumps, json_loads=json_loads, **connection_params
        )
        connectors.append(connector)
        if open:
            await connector.open_async()
        return connector

    yield _
    for connector in connectors:
        await connector.close_async()


@pytest.fixture
async def aiopg_connector(aiopg_connector_factory) -> aiopg.AiopgConnector:
    return await aiopg_connector_factory()
