import sys
import types

import pytest

from procrastinate import exceptions, utils


def test_load_from_path():
    loads = utils.load_from_path("json.loads", types.FunctionType)
    import json

    assert loads is json.loads


@pytest.mark.parametrize("input", ["foobarbaz", "fooobarbaz.loads", "json.foobarbaz"])
def test_load_from_path_error(input):
    with pytest.raises(ImportError):
        utils.load_from_path(input, types.FunctionType)


def test_load_from_path_wrong_type():
    with pytest.raises(exceptions.LoadFromPathError):
        utils.load_from_path("json.loads", int)


def test_import_all():
    module = "tests.unit.unused_module"
    assert module not in sys.modules

    utils.import_all([module])

    assert module in sys.modules


def test_sync_await():
    result = []

    async def coro():
        result.append(1)

    utils.sync_await(coro())

    assert result == [1]


def test_add_sync_api():
    result = []

    @utils.add_sync_api
    class Test:
        def a(self):
            result.append("a")

        def b_async(self):
            result.append("b")

        async def c(self):
            result.append("c")

        async def d_async(self):
            result.append("d")

    test = Test()
    funcs = dir(test)
    assert "a" in funcs
    assert "a_async" not in funcs
    assert "b" not in funcs
    assert "b_async" in funcs
    assert "c" in funcs
    assert "c_async" not in funcs
    assert "d" in funcs
    assert "d_async" in funcs

    test.a()
    test.b_async()
    test.d()

    assert result == ["a", "b", "d"]


# Event loops are not reentrant, so we can't call .d() from above
# in an asyncio test, and we can't call await .a_async() from below
# outside of an asyncio test. Consequently, we need 2 distinct tests.
@pytest.mark.asyncio
async def test_add_sync_api_does_not_break_original_coroutine():
    result = []

    @utils.add_sync_api
    class Test:
        async def a_async(self):
            result.append("a")

    await Test().a_async()

    assert result == ["a"]


@pytest.mark.asyncio
async def test_add_sync_api_classmethods_async():
    result = []

    @utils.add_sync_api
    class Test:
        @classmethod
        async def a_async(cls, value):
            result.extend([cls, value])

    await Test.a_async("async")

    assert result == [Test, "async"]


def test_add_sync_api_classmethods_sync():
    result = []

    @utils.add_sync_api
    class Test:
        @classmethod
        async def a_async(cls, value):
            result.extend([cls, value])

    Test.a("sync")

    assert result == [Test, "sync"]


@pytest.mark.asyncio
async def test_add_sync_api_staticmethods_async():
    result = []

    @utils.add_sync_api
    class Test:
        @staticmethod
        async def a_async(value):
            result.append(value)

    await Test.a_async("async")

    assert result == ["async"]


def test_add_sync_api_staticmethods_sync():
    result = []

    @utils.add_sync_api
    class Test:
        @staticmethod
        async def a_async(value):
            result.append(value)

    Test.a("sync")

    assert result == ["sync"]


def test_add_sync_api_invalid():
    # This test gives the decorator an object that looks like an async method
    # but is not. Given it's neither a method nor a classmethod nor a staticmethod
    # but a NotAMethod(), it should be detected as such.
    class NotAMethod:
        async def __func__():
            pass

    with pytest.raises(ValueError):

        @utils.add_sync_api
        class Test:
            a_async = NotAMethod()


def test_causes():
    e1, e2, e3 = AttributeError("foo"), KeyError("bar"), IndexError("baz")

    try:
        try:
            # e3 will be e2's __cause__
            raise e2 from e3
        except Exception:
            # e2 will be e1's __context__
            raise e1
    except Exception as exc2:
        result = list(utils.causes(exc2))

    assert result == [e1, e2, e3]
