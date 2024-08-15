from __future__ import annotations

import pytest
from django import db as django_db
from psycopg import errors as psycopg_errors

from procrastinate import exceptions
from procrastinate.contrib.django import django_connector as django_connector_module


def test_wrap_exceptions__no_cause():
    with pytest.raises(django_db.DatabaseError):
        with django_connector_module.wrap_exceptions():
            raise django_db.DatabaseError


def test_wrap_exceptions__with_cause():
    with pytest.raises(exceptions.ConnectorException):
        with django_connector_module.wrap_exceptions():
            raise django_db.DatabaseError from psycopg_errors.Error()
