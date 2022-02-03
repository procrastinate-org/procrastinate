import functools
import json

import attr
import pytest

from procrastinate.contrib.django import django_connector

pytestmark = pytest.mark.asyncio


@pytest.fixture
def django_connector_factory(connection_params, django_db):
    connectors = []

    def _(**kwargs):
        json_dumps = kwargs.pop("json_dumps", None)
        json_loads = kwargs.pop("json_loads", None)
        connection_params.update(kwargs)
        connector = django_connector.DjangoConnector(
            json_dumps=json_dumps, json_loads=json_loads, **connection_params
        )
        connectors.append(connector)
        connector.open()
        return connector

    yield _
    for connector in connectors:
        connector.close()


@pytest.mark.parametrize(
    "method_name, expected",
    [
        ("execute_query_one", {"json": {"a": "a", "b": "foo"}}),
        ("execute_query_all", [{"json": {"a": "a", "b": "foo"}}]),
    ],
)
def test_execute_query_json_dumps(
    django_connector_factory, mocker, method_name, expected
):
    class NotJSONSerializableByDefault:
        pass

    def encode(obj):
        if isinstance(obj, NotJSONSerializableByDefault):
            return "foo"
        raise TypeError()

    query = "SELECT %(arg)s::jsonb as json"
    arg = {"a": "a", "b": NotJSONSerializableByDefault()}
    json_dumps = functools.partial(json.dumps, default=encode)
    connector = django_connector_factory(json_dumps=json_dumps)
    method = getattr(connector, method_name)

    result = method(query, arg=arg)
    assert result == expected


def test_json_loads(django_connector_factory, mocker):
    @attr.dataclass
    class Param:
        p: int

    def decode(dct):
        if "b" in dct:
            dct["b"] = Param(p=dct["b"])
        return dct

    json_loads = functools.partial(json.loads, object_hook=decode)

    query = "SELECT %(arg)s::jsonb as json"
    arg = {"a": 1, "b": 2}
    connector = django_connector_factory(json_loads=json_loads)

    result = connector.execute_query_one(query, arg=arg)
    assert result["json"] == {"a": 1, "b": Param(p=2)}


def test_execute_query(django_connector):
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


def test_execute_query_percent(django_connector):
    django_connector.execute_query("SELECT '%'")
    result = django_connector.execute_query_one("SELECT '%'")
    assert result == {"?column?": "%"}

    result = django_connector.execute_query_all("SELECT '%'")
    assert result == [{"?column?": "%"}]


def test_execute_query_no_interpolate(django_connector):
    result = django_connector.execute_query_one("SELECT '%(foo)s' as foo;")
    assert result == {"foo": "%(foo)s"}


def test_execute_query_interpolate(django_connector):
    result = django_connector.execute_query_one("SELECT %(foo)s as foo;", foo="bar")
    assert result == {"foo": "bar"}


def test_close(django_connector):
    django_connector.execute_query("SELECT 1")
    django_connector.close()


# TODO test wait_for_notification, separate process may execute notify
