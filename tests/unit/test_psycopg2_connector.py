import psycopg2
import pytest

from procrastinate import exceptions, psycopg2_connector


def test_wrap_exceptions_wraps():
    @psycopg2_connector.wrap_exceptions
    def func():
        raise psycopg2.DatabaseError

    with pytest.raises(exceptions.ConnectorException):
        func()


def test_wrap_exceptions_success():
    @psycopg2_connector.wrap_exceptions
    def func(a, b):
        return a, b

    assert func(1, 2) == (1, 2)


def test_wrap_query_exceptions_reached_max_tries(mocker):
    called = []

    @psycopg2_connector.wrap_query_exceptions
    def func(connector):
        called.append(True)
        raise psycopg2.errors.InterfaceError("connection already closed")

    connector = mocker.Mock(_pool=mocker.Mock(maxconn=5))

    with pytest.raises(exceptions.ConnectorException) as excinfo:
        func(connector)

    assert len(called) == 6
    assert str(excinfo.value) == "Could not get a valid connection after 6 tries"


@pytest.mark.parametrize("exception_class", [Exception, psycopg2.errors.InterfaceError])
def test_wrap_query_exceptions_unhandled_exception(mocker, exception_class):
    called = []

    @psycopg2_connector.wrap_query_exceptions
    def func(connector):
        called.append(True)
        raise exception_class("foo")

    connector = mocker.Mock(_pool=mocker.Mock(maxconn=5))

    with pytest.raises(exception_class):
        func(connector)

    assert len(called) == 1


def test_wrap_query_exceptions_success(mocker):
    called = []

    @psycopg2_connector.wrap_query_exceptions
    def func(connector, a, b):
        if len(called) < 2:
            called.append(True)
            raise psycopg2.errors.InterfaceError("connection already closed")
        return a, b

    connector = mocker.Mock(_pool=mocker.Mock(maxconn=5))
    assert func(connector, 1, 2) == (1, 2)
    assert len(called) == 2


@pytest.mark.parametrize(
    "method_name",
    ["__init__", "close", "execute_query", "execute_query_one", "execute_query_all"],
)
def test_wrap_exceptions_applied(method_name):
    connector = psycopg2_connector.Psycopg2Connector()
    assert getattr(connector, method_name)._exceptions_wrapped is True
