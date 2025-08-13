from __future__ import annotations

import pytest
from django import db as django_db
from psycopg import errors as psycopg_errors

from procrastinate import exceptions
from procrastinate.contrib.django import django_connector as django_connector_module
from procrastinate.psycopg_connector import PsycopgConnector


def test_wrap_exceptions__no_cause():
    with pytest.raises(django_db.DatabaseError):
        with django_connector_module.wrap_exceptions():
            raise django_db.DatabaseError


def test_wrap_exceptions__with_cause():
    with pytest.raises(exceptions.ConnectorException):
        with django_connector_module.wrap_exceptions():
            raise django_db.DatabaseError from psycopg_errors.Error()


def test_get_worker_connector():
    django_connector = django_connector_module.DjangoConnector()
    worker_connector = django_connector.get_worker_connector()
    assert isinstance(worker_connector, PsycopgConnector)
    assert worker_connector._pool_kwargs == {"min_size": 1, "max_size": 4}
