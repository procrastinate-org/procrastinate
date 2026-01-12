from __future__ import annotations

import asyncio
import datetime
import functools
import logging
import sys
import time
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

    utils.async_to_sync(coro)

    assert result == [1]


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


def test_get_full_path_partial():
    with pytest.raises(exceptions.FunctionPathError):
        utils.get_full_path(functools.partial(test_get_full_path_partial))


# `launched` and `finished` are sets used by the run_tasks tests, both coro and
# callback write to these sets, and the tests themselves read from these sets.


@pytest.fixture
def launched():
    return set()


@pytest.fixture
def finished():
    return set()


@pytest.fixture
def short():
    before = time.time()
    yield
    after = time.time()
    assert after - before < 0.1


@pytest.fixture
def coro(launched, finished):
    async def func(name, *, sleep=0, exc=None):
        launched.add(name)
        await asyncio.sleep(sleep)
        finished.add(name)
        if exc:
            raise exc

    return func


@pytest.fixture
def callback(launched):
    # this fixture returns a "callback generator" function: call it and you
    # get a callback function in return
    def _(name):
        def __():
            launched.add(name)

        return __

    return _


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
def awaitable_context():
    awaited = []

    async def open():
        awaited.append("open")

    async def close():
        awaited.append("closed")

    context = utils.AwaitableContext(open_coro=open, close_coro=close, return_value=1)
    context.awaited = awaited  # type: ignore
    return context


async def test_awaitable_context_await(awaitable_context):
    return_value = await awaitable_context

    assert return_value == 1
    assert awaitable_context.awaited == ["open"]


async def test_awaitable_context_enter_exit(awaitable_context):
    async with awaitable_context as return_value:
        pass

    assert return_value == 1
    assert awaitable_context.awaited == ["open", "closed"]


def test_caller_module_name():
    assert utils.caller_module_name() == __name__


def test_check_stack_failure(mocker):
    mocker.patch("inspect.currentframe", return_value=None)
    with pytest.raises(exceptions.CallerModuleUnknown):
        assert utils.caller_module_name()


def test_import_or_wrapper__ok():
    result = list(utils.import_or_wrapper("json", "csv"))
    import csv
    import json

    assert result == [json, csv]


def test_import_or_wrapper__fail():
    (result,) = utils.import_or_wrapper("a" * 30)

    with pytest.raises(ImportError):
        assert result.foo


def test_moved_elsewhere():
    me = utils.MovedElsewhere(name="foo", new_location="bar")
    with pytest.raises(
        exceptions.MovedElsewhere,
        match=r"procrastinate\.foo has been moved to bar",
    ):
        me.foo


def test_moved_elsewhere__call():
    me = utils.MovedElsewhere(name="foo", new_location="bar")
    with pytest.raises(
        exceptions.MovedElsewhere,
        match=r"procrastinate\.foo has been moved to bar",
    ):
        me()


async def test_async_gen_timeout():
    async def gen():
        yield 1
        await asyncio.sleep(0.2)
        yield 2
        yield 3

    with pytest.raises(asyncio.TimeoutError):
        async for _ in utils.gen_with_timeout(
            aiterable=gen(), timeout=0.1, raise_timeout=True
        ):
            pass


async def test_async_gen_timeout__no_raise():
    async def gen():
        yield 1
        await asyncio.sleep(0.2)
        yield 2
        yield 3

    result = []
    async for i in utils.gen_with_timeout(
        aiterable=gen(), timeout=0.1, raise_timeout=False
    ):
        result.append(i)

    assert result == [1]


async def test_async_gen_timeout__complete():
    async def gen():
        yield 1
        yield 2
        yield 3

    result = []
    async for i in utils.gen_with_timeout(
        aiterable=gen(), timeout=0.1, raise_timeout=False
    ):
        result.append(i)

    assert result == [1, 2, 3]


async def test_async_context_decorator():
    result = []

    @utils.async_context_decorator
    async def func():
        result.append(1)
        yield
        result.append(3)

    @func()
    async def func2():
        result.append(2)
        return 4

    assert await func2() == 4

    assert result == [1, 2, 3]


@pytest.mark.parametrize(
    "task_1_error, task_2_error",
    [
        (None, None),
        (ValueError("Nope from task_1"), None),
        (None, ValueError("Nope from task_2")),
        (ValueError("Nope from task_1"), ValueError("Nope from task_2")),
    ],
)
async def test_cancel_and_capture_errors(task_1_error, task_2_error, caplog):
    caplog.set_level(logging.ERROR)

    async def task_1():
        if task_1_error:
            raise task_1_error
        else:
            await asyncio.sleep(0.5)

    async def task_2():
        if task_2_error:
            raise task_2_error
        else:
            await asyncio.sleep(0.5)

    tasks = [asyncio.create_task(task_1()), asyncio.create_task(task_2())]
    await asyncio.sleep(0.01)
    await asyncio.wait_for(utils.cancel_and_capture_errors(tasks), timeout=100)

    expected_error_count = sum(1 for error in (task_1_error, task_2_error) if error)

    assert len(caplog.records) == expected_error_count


@pytest.mark.parametrize(
    "queues, result", [(None, "all queues"), (["foo", "bar"], "queues foo, bar")]
)
def test_queues_display(queues, result):
    assert utils.queues_display(queues) == result
