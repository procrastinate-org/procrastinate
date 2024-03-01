from __future__ import annotations

import pytest
from django.core import exceptions

from procrastinate import psycopg_connector
from procrastinate.contrib.aiopg import aiopg_connector
from procrastinate.contrib.django import django_connector as django_connector_module


@pytest.fixture
def django_connector(db):
    return django_connector_module.DjangoConnector(alias="default")


def test_get_sync_connector(django_connector):
    assert django_connector.get_sync_connector() is django_connector


def test_open(django_connector):
    assert django_connector.open() is None


def test_open_pool(django_connector):
    with pytest.raises(exceptions.ImproperlyConfigured):
        django_connector.open(pool=object())


def test_close(django_connector):
    assert django_connector.close() is None


async def test_open_async(django_connector):
    assert await django_connector.open_async() is None


async def test_open_pool_async(django_connector):
    with pytest.raises(exceptions.ImproperlyConfigured):
        await django_connector.open_async(pool=object())


async def test_close_async(django_connector):
    assert await django_connector.close_async() is None


async def test_execute_query_async(django_connector):
    assert (
        await django_connector.execute_query_async(
            "COMMENT ON TABLE \"procrastinate_jobs\" IS 'foo' "
        )
        is None
    )
    result = await django_connector.execute_query_one_async(
        "SELECT obj_description('public.procrastinate_jobs'::regclass)"
    )
    assert result == {"obj_description": "foo"}

    result = await django_connector.execute_query_all_async(
        "SELECT obj_description('public.procrastinate_jobs'::regclass)"
    )
    assert result == [{"obj_description": "foo"}]


def test_execute_query_sync(django_connector):
    assert (
        django_connector.execute_query(
            "COMMENT ON TABLE \"procrastinate_jobs\" IS 'foo' "
        )
        is None
    )
    result = django_connector.execute_query_one(
        "SELECT obj_description('public.procrastinate_jobs'::regclass)"
    )
    assert result == {"obj_description": "foo"}

    result = django_connector.execute_query_all(
        "SELECT obj_description('public.procrastinate_jobs'::regclass)"
    )
    assert result == [{"obj_description": "foo"}]


@pytest.mark.parametrize(
    "installed, type",
    [
        ({"psycopg"}, psycopg_connector.PsycopgConnector),
        ({"aiopg"}, aiopg_connector.AiopgConnector),
    ],
)
async def test_get_worker_connector(installed, type, django_connector, mocker):
    def package_is_installed(name):
        return name in installed

    mocker.patch(
        "procrastinate.contrib.django.utils.package_is_installed",
        side_effect=package_is_installed,
    )

    connector = django_connector.get_worker_connector()

    assert isinstance(connector, type)

    await connector.open_async()
    try:
        assert await connector.execute_query_one_async("SELECT 1 as x") == {"x": 1}
    finally:
        await connector.close_async()


async def test_get_worker_connector__error(django_connector, mocker):
    mocker.patch(
        "procrastinate.contrib.django.utils.package_is_installed",
        return_value=False,
    )

    with pytest.raises(exceptions.ImproperlyConfigured):
        django_connector.get_worker_connector()
