import asyncio
import datetime
import functools
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


async def test_run_tasks(finished, coro, short, caplog):
    caplog.set_level("ERROR")
    # Two functions in main coros, both go through their ends
    await utils.run_tasks(main_coros=[coro(1), coro(2, sleep=0.01)])
    assert finished == {1, 2}

    assert caplog.records == []


async def test_run_tasks_graceful_stop_callback_not_called(
    launched, coro, callback, short
):
    # A graceful_stop_callback is provided but isn't used because the main
    # coros return on their own.
    await utils.run_tasks(main_coros=[coro(1)], graceful_stop_callback=callback(2))
    assert launched == {1}


async def test_run_tasks_graceful_stop_callback_called(launched, coro, callback, short):
    # A main function is provided, but it crashes. This time, the graceful callback
    # is called.
    with pytest.raises(exceptions.RunTaskError):
        await utils.run_tasks(
            main_coros=[coro(1, exc=ZeroDivisionError)],
            graceful_stop_callback=callback(2),
        )
    assert launched == {1, 2}


async def test_run_tasks_graceful_stop_callback_called_side(
    launched, finished, coro, callback, short
):
    # Two main coros provided, one crashes and one succeeds. The
    # graceful_stop_callback is called and the coro that succeeds is awaited
    # until it returns
    with pytest.raises(exceptions.RunTaskError):
        await utils.run_tasks(
            main_coros=[coro(1, sleep=0.01), coro(2, exc=ZeroDivisionError)],
            graceful_stop_callback=callback(3),
        )
    assert launched == {1, 2, 3}
    assert finished == {1, 2}


async def test_run_tasks_side_coro(launched, finished, coro, short):
    # When all the main coros have returned, the remaining side coros are
    # cancelled
    await utils.run_tasks(main_coros=[coro(1), coro(2)], side_coros=[coro(3, sleep=1)])
    assert launched == {1, 2, 3}
    assert finished == {1, 2}


async def test_run_tasks_side_coro_crash(launched, finished, coro, short):
    # There's a main and a side. The side crashes. Main is still awaited and
    # the unction raises
    with pytest.raises(exceptions.RunTaskError) as exc_info:
        await utils.run_tasks(
            main_coros=[coro(1, sleep=0.01)],
            side_coros=[coro(2, exc=ZeroDivisionError)],
        )
    assert launched == {1, 2}
    assert finished == {1, 2}
    assert isinstance(exc_info.value.__cause__, ZeroDivisionError)


async def test_run_tasks_main_coro_crash(launched, finished, coro, short):
    # There's a main and a side. The main crashes. Side is cancelled, and the
    # function raises
    with pytest.raises(exceptions.RunTaskError) as exc_info:
        await utils.run_tasks(
            main_coros=[coro(1, exc=ZeroDivisionError)],
            side_coros=[coro(2, sleep=1)],
        )
    assert launched == {1, 2}
    assert finished == {1}
    assert isinstance(exc_info.value.__cause__, ZeroDivisionError)


async def test_run_tasks_main_coro_one_crashes(launched, finished, coro, short):
    # 2 mains. One main crashes. The other finishes, and then the function fails.
    with pytest.raises(exceptions.RunTaskError) as exc_info:
        await utils.run_tasks(
            main_coros=[coro(1, exc=ZeroDivisionError), coro(2, sleep=0.001)],
        )
    assert launched == {1, 2}
    assert finished == {1, 2}
    assert isinstance(exc_info.value.__cause__, ZeroDivisionError)


async def test_run_tasks_main_coro_both_crash(launched, finished, coro, short):
    # 2 mains. The 2 crash. The reported error is for the first one.
    with pytest.raises(exceptions.RunTaskError) as exc_info:
        await utils.run_tasks(
            main_coros=[
                coro(1, sleep=0.001, exc=ValueError),
                coro(2, exc=ZeroDivisionError),
            ],
        )
    assert launched == {1, 2}
    assert finished == {1, 2}
    assert isinstance(exc_info.value.__cause__, ValueError)


@pytest.fixture
def count_logs(caplog):
    """Count how many logs match all the arguments"""
    caplog.set_level("DEBUG")

    def _(**kwargs):
        return sum(
            all((getattr(record, key, None) == value) for key, value in kwargs.items())
            for record in caplog.records
        )

    return _


async def test_run_tasks_logs(coro, short, count_logs):
    # 2 mains. The 2 crash. The reported error is for the first one.
    with pytest.raises(exceptions.RunTaskError):
        await utils.run_tasks(
            main_coros=[
                coro(1, exc=ZeroDivisionError("foo")),
                coro(2),
            ],
            side_coros=[
                coro(3, exc=RuntimeError("bar")),
                coro(4),
            ],
        )
    assert 4 == count_logs(
        levelname="DEBUG",
        message="Started func",
        action="func_start",
    )

    assert 1 == count_logs(
        levelname="DEBUG",
        message="func finished execution",
        action="func_stop",
    )

    assert 1 == count_logs(
        levelname="ERROR",
        message="func error: ZeroDivisionError('foo')",
        action="func_error",
    )

    assert 1 == count_logs(
        levelname="ERROR",
        message="func error: RuntimeError('bar')",
        action="func_error",
    )


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
    context.awaited = awaited
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
