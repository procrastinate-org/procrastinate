import psycopg2
import pytest

from procrastinate import exceptions, psycopg2_connector


@pytest.mark.asyncio
def test_wrap_exceptions_wraps():
    @psycopg2_connector.wrap_exceptions
    def func():
        raise psycopg2.DatabaseError

    with pytest.raises(exceptions.ConnectorException):
        func()


@pytest.mark.asyncio
async def test_wrap_exceptions_success():
    @psycopg2_connector.wrap_exceptions
    def func(a, b):
        return a, b

    assert func(1, 2) == (1, 2)


@pytest.mark.parametrize(
    "method_name",
    ["__init__", "close", "execute_query", "execute_query_one", "execute_query_all"],
)
def test_wrap_exceptions_applied(method_name):
    connector = psycopg2_connector.Psycopg2Connector()
    assert getattr(connector, method_name)._exceptions_wrapped is True
