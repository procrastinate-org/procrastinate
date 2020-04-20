import pytest

from procrastinate import aiopg_connector


@pytest.mark.asyncio
async def test_adapt_pool_args_on_connect(mocker):
    called = []

    async def on_connect(connection):
        called.append(connection)

    args = aiopg_connector.PostgresConnector._adapt_pool_args(
        pool_args={"on_connect": on_connect}, json_loads=None
    )

    assert args["on_connect"] is not on_connect

    connection = mocker.Mock()
    await args["on_connect"](connection)

    assert called == [connection]


def test_adapt_pool_args_maxsize():
    args = aiopg_connector.PostgresConnector._adapt_pool_args(
        pool_args={"maxsize": 1}, json_loads=None
    )

    assert args["maxsize"] == 2
