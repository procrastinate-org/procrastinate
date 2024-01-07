import psycopg
import pytest

from procrastinate import exceptions, sync_psycopg_connector


def test_wrap_exceptions_wraps():
    @sync_psycopg_connector.wrap_exceptions
    def func():
        raise psycopg.DatabaseError

    with pytest.raises(exceptions.ConnectorException):
        func()


def test_wrap_exceptions_success():
    @sync_psycopg_connector.wrap_exceptions
    def func(a, b):
        return a, b

    assert func(1, 2) == (1, 2)


@pytest.mark.parametrize(
    "method_name",
    [
        "_create_pool",
        "close",
        "execute_query",
        "execute_query_one",
        "execute_query_all",
    ],
)
def test_wrap_exceptions_applied(method_name):
    connector = sync_psycopg_connector.SyncPsycopgConnector()
    assert getattr(connector, method_name)._exceptions_wrapped is True


@pytest.fixture
def mock_create_pool(mocker):
    return mocker.patch.object(
        sync_psycopg_connector.SyncPsycopgConnector, "_create_pool"
    )


def test_open_no_pool_specified(mock_create_pool):
    connector = sync_psycopg_connector.SyncPsycopgConnector()

    connector.open()

    assert connector._pool_externally_set is False
    mock_create_pool.assert_called_once_with(connector._pool_args)


def test_open_pool_argument_specified(mock_create_pool, mocker):
    connector = sync_psycopg_connector.SyncPsycopgConnector()

    pool = mocker.MagicMock()
    connector.open(pool)

    assert connector._pool_externally_set is True
    mock_create_pool.assert_not_called()
    assert connector._pool == pool


def test_get_pool():
    connector = sync_psycopg_connector.SyncPsycopgConnector()

    with pytest.raises(exceptions.AppNotOpen):
        _ = connector.pool
