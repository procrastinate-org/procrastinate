import psycopg2
import pytest
import sqlalchemy

from procrastinate import exceptions
from procrastinate.contrib.sqlalchemy import (
    psycopg2_connector as sqlalchemy_psycopg2_connector,
)


def test_wrap_exceptions_wraps():
    @sqlalchemy_psycopg2_connector.wrap_exceptions
    def func():
        raise sqlalchemy.exc.OperationalError(
            statement="SELECT 1", params={}, orig=psycopg2.DatabaseError()
        )

    with pytest.raises(exceptions.ConnectorException):
        func()


def test_wrap_exceptions_unique_violation(mocker):
    class UniqueViolation(psycopg2.errors.UniqueViolation):
        diag = None

    @sqlalchemy_psycopg2_connector.wrap_exceptions
    def func():
        exc = UniqueViolation()
        exc.diag = mocker.Mock(constraint_name="constraint name")
        raise sqlalchemy.exc.IntegrityError(statement="SELECT 1", params={}, orig=exc)

    with pytest.raises(exceptions.UniqueViolation) as excinfo:
        func()

    assert excinfo.value.constraint_name == "constraint name"


def test_wrap_exceptions_success():
    @sqlalchemy_psycopg2_connector.wrap_exceptions
    def func(a, b):
        return a, b

    assert func(1, 2) == (1, 2)


def test_wrap_query_exceptions_retry():
    call_count = 0

    @sqlalchemy_psycopg2_connector.wrap_query_exceptions
    def func():
        nonlocal call_count
        call_count += 1
        raise sqlalchemy.exc.DBAPIError(
            statement="SELECT 1",
            params={},
            orig=psycopg2.errors.AdminShutdown(),
            connection_invalidated=True,
        )

    with pytest.raises(sqlalchemy.exc.DBAPIError):
        func()

    assert call_count == 2


def test_wrap_query_exceptions_unhandled_exception():
    call_count = 0

    @sqlalchemy_psycopg2_connector.wrap_query_exceptions
    def func():
        nonlocal call_count
        call_count += 1
        raise sqlalchemy.exc.OperationalError(
            statement="SELECT 1",
            params={},
            orig=psycopg2.errors.OperationalError(),
        )

    with pytest.raises(sqlalchemy.exc.OperationalError):
        func()

    assert call_count == 1


def test_wrap_query_exceptions_success(mocker):
    call_count = 0

    @sqlalchemy_psycopg2_connector.wrap_query_exceptions
    def func(a, b):
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            raise sqlalchemy.exc.DBAPIError(
                statement="SELECT 1",
                params={},
                orig=psycopg2.errors.AdminShutdown(),
                connection_invalidated=True,
            )
        return a, b

    assert func(1, 2) == (1, 2)
    assert call_count == 2


@pytest.mark.parametrize(
    "method_name",
    [
        "open",
        "close",
        "execute_query",
        "execute_query_one",
        "execute_query_all",
    ],
)
def test_wrap_exceptions_applied(method_name):
    connector = sqlalchemy_psycopg2_connector.SQLAlchemyPsycopg2Connector()
    assert getattr(connector, method_name)._exceptions_wrapped is True


@pytest.fixture
def mock_create_engine(mocker):
    return mocker.patch.object(
        sqlalchemy_psycopg2_connector.SQLAlchemyPsycopg2Connector, "_create_engine"
    )


def test_open_no_pool_specified(mock_create_engine):
    connector = sqlalchemy_psycopg2_connector.SQLAlchemyPsycopg2Connector()

    connector.open()

    assert connector._engine_externally_set is False
    mock_create_engine.assert_called_once_with(
        connector._engine_dsn, connector._engine_kwargs
    )


def test_open_pool_argument_specified(engine, mock_create_engine):
    connector = sqlalchemy_psycopg2_connector.SQLAlchemyPsycopg2Connector()

    connector.open(engine)

    assert connector._engine_externally_set is True
    mock_create_engine.assert_not_called()
    assert connector.engine == engine


def test_get_engine():
    connector = sqlalchemy_psycopg2_connector.SQLAlchemyPsycopg2Connector()

    with pytest.raises(exceptions.AppNotOpen):
        _ = connector.engine
