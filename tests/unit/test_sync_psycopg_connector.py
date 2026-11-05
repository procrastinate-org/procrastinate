from __future__ import annotations

import psycopg
import pytest

from procrastinate import exceptions, manager, sync_psycopg_connector


def test_wrap_exceptions_wraps():
    @sync_psycopg_connector.wrap_exceptions()
    def func():
        raise psycopg.DatabaseError

    with pytest.raises(exceptions.ConnectorException):
        func()


class _FakeUniqueViolation(psycopg.errors.UniqueViolation):
    # ``diag`` is a read-only property on the real exception, backed by a libpq
    # result that we can't easily fabricate offline, so we override it here.
    def __init__(self, constraint_name, message_detail):
        super().__init__("duplicate key value violates ...")
        self._fake_diag = type(
            "FakeDiag",
            (),
            {"constraint_name": constraint_name, "message_detail": message_detail},
        )()

    @property
    def diag(self):
        return self._fake_diag


def _make_unique_violation(constraint_name, message_detail):
    return _FakeUniqueViolation(constraint_name, message_detail)


@pytest.mark.parametrize(
    "message_detail",
    [
        # English (default lc_messages)
        pytest.param("Key (queueing_lock)=(some_lock) already exists.", id="english"),
        # Russian (lc_messages=ru_RU.UTF-8): the "Key" prefix is translated but
        # the "(columns)=(values)" structure is not. See issue #1531.
        pytest.param(
            'Ключ "(queueing_lock)=(some_lock)" уже существует.', id="russian"
        ),
    ],
)
def test_wrap_exceptions_queueing_lock_locale_agnostic(message_detail):
    @sync_psycopg_connector.wrap_exceptions()
    def func():
        raise _make_unique_violation(manager.QUEUEING_LOCK_CONSTRAINT, message_detail)

    with pytest.raises(exceptions.UniqueViolation) as excinfo:
        func()

    assert excinfo.value.constraint_name == manager.QUEUEING_LOCK_CONSTRAINT
    assert excinfo.value.queueing_lock == "some_lock"


def test_wrap_exceptions_queueing_lock_unparseable_detail():
    # Even if the queueing lock cannot be extracted from the (possibly
    # translated) error detail, a UniqueViolation must still be raised instead
    # of a bare AssertionError (issue #1531).
    @sync_psycopg_connector.wrap_exceptions()
    def func():
        raise _make_unique_violation(
            manager.QUEUEING_LOCK_CONSTRAINT, "unexpected detail format"
        )

    with pytest.raises(exceptions.UniqueViolation) as excinfo:
        func()

    assert excinfo.value.constraint_name == manager.QUEUEING_LOCK_CONSTRAINT
    assert excinfo.value.queueing_lock is None


def test_wrap_exceptions_success():
    @sync_psycopg_connector.wrap_exceptions()
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
    assert hasattr(getattr(connector, method_name), "__wrapped__")


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
