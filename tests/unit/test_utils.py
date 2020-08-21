import asyncio
import datetime
import sys
import types

import pytest

from procrastinate import exceptions, utils
from tests.unit.conftest import AsyncMock


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


def test_get_module_name_path1():
    # Calling the function on itself
    assert utils._get_module_name(utils._get_module_name) == "procrastinate.utils"


def test_get_module_name_path2():
    def yay():
        pass

    yay.__module__ = "__main__"
    # We're probably doing strange things to the pytest binary
    # but it's probably harmless
    del sys.modules["__main__"].__file__

    # Calling the function on itself
    assert utils._get_module_name(yay) == "__main__"


def test_get_module_name_path3():
    def yay():
        pass

    yay.__module__ = "__main__"
    sys.modules["__main__"].__file__ = "/home"

    # Calling the function on itself
    assert utils._get_module_name(yay) == "__main__"


def test_get_module_name_path4():
    def yay():
        pass

    yay.__module__ = "__main__"
    sys.modules["__main__"].__file__ = "a/b.py"

    # Calling the function on itself
    assert utils._get_module_name(yay) == "a.b"


def test_get_full_path():
    path = "procrastinate.utils.get_full_path"
    # Calling the function on itself
    assert utils.get_full_path(utils.get_full_path) == path


@pytest.mark.asyncio
async def test_task_context_exit_normally(caplog):
    done = []

    async def foo():
        done.append(True)

    with utils.task_context(foo(), name="foo"):
        await asyncio.sleep(0)

    assert done == [True]


@pytest.mark.asyncio
async def test_task_context_cancelled(caplog):
    done = []

    async def foo():
        done.append(True)
        await asyncio.sleep(10)

    caplog.set_level("DEBUG")

    with utils.task_context(foo(), name="foo") as task:
        await asyncio.sleep(0)

    assert done == [True]
    # Give the task a cycle to update
    await asyncio.sleep(0)
    assert task.cancelled() is True

    assert len([r for r in caplog.records if r.action == "foo_stop"]) == 1


@pytest.mark.asyncio
async def test_task_context_exception(caplog):
    async def foo():
        0 / 0

    with utils.task_context(foo(), name="foo") as task:
        await asyncio.sleep(0)

    # Give the task a cycled to update
    await asyncio.sleep(0)
    assert task.done() is True

    exc_logs = [r for r in caplog.records if r.action == "foo_error" and r.exc_info]
    assert len(exc_logs) == 1


def test_utcnow(mocker):
    dt = mocker.patch("datetime.datetime")
    assert utils.utcnow() == dt.now.return_value
    dt.now.assert_called_once_with(tz=datetime.timezone.utc)


@pytest.mark.parametrize(
    "input, expected",
    [
        (
            "2020-01-05",
            datetime.datetime(2020, 1, 5, 0, 0, tzinfo=datetime.timezone.utc),
        ),
        (
            "2020/01/05",
            datetime.datetime(2020, 1, 5, 0, 0, tzinfo=datetime.timezone.utc),
        ),
        (
            "2020/01/05 22:07",
            datetime.datetime(2020, 1, 5, 22, 7, tzinfo=datetime.timezone.utc),
        ),
        (
            "1984-06-02 19:05:57",
            datetime.datetime(1984, 6, 2, 19, 5, 57, tzinfo=datetime.timezone.utc),
        ),
        (
            "1984-06-02T19:05:57.720Z",
            datetime.datetime(
                1984, 6, 2, 19, 5, 57, 720000, tzinfo=datetime.timezone.utc
            ),
        ),
        (
            "1984-06-02T19:05:57.720+01:00",
            datetime.datetime(
                1984,
                6,
                2,
                19,
                5,
                57,
                720000,
                tzinfo=datetime.timezone(datetime.timedelta(hours=1)),
            ),
        ),
    ],
)
def test_parse_datetime(input, expected):
    assert utils.parse_datetime(input) == expected


@pytest.fixture
def mock_awaitable_context():
    open_mock, close_mock = AsyncMock(), AsyncMock()
    return utils.AwaitableContext(
        open_coro=lambda: open_mock, close_coro=lambda: close_mock, return_value=1,
    )


@pytest.mark.asyncio
async def test_awaitable_context_await(mock_awaitable_context):
    return_value = await mock_awaitable_context

    assert return_value == 1
    assert mock_awaitable_context._open_coro().was_awaited
    assert not mock_awaitable_context._close_coro().was_awaited


@pytest.mark.asyncio
async def test_awaitable_context_enter_exit(mock_awaitable_context):
    async with mock_awaitable_context as return_value:
        pass

    assert return_value == 1
    assert mock_awaitable_context._open_coro().was_awaited
    assert mock_awaitable_context._close_coro().was_awaited
