from __future__ import annotations

import asyncio
import datetime
import importlib
import inspect
import logging
import pathlib
import types
from typing import (
    Any,
    AsyncGenerator,
    AsyncIterator,
    Awaitable,
    Callable,
    Coroutine,
    Generic,
    Iterable,
    TypeVar,
)

import attr
import dateutil.parser
from asgiref import sync

from procrastinate import exceptions

T = TypeVar("T")
U = TypeVar("U")

logger = logging.getLogger(__name__)


def load_from_path(path: str, allowed_type: type[T] | None = None) -> T:
    """
    Import and return then object at the given full python path.
    """
    if "." not in path:
        raise exceptions.LoadFromPathError(f"{path} is not a valid path")
    module_path, name = path.rsplit(".", 1)
    try:
        module = importlib.import_module(module_path)
    except ImportError as exc:
        raise exceptions.LoadFromPathError(str(exc)) from exc

    try:
        imported = getattr(module, name)
    except AttributeError as exc:
        raise exceptions.LoadFromPathError(str(exc)) from exc

    if allowed_type and not isinstance(imported, allowed_type):
        raise exceptions.LoadFromPathError(
            f"Object at {path} is not of type {allowed_type.__name__} "
            f"but {type(imported).__name__}"
        )

    return imported


def import_all(import_paths: Iterable[str]) -> None:
    """
    Given a list of paths, just import them all
    """
    for import_path in import_paths:
        logger.debug(
            f"Importing module {import_path}",
            extra={"action": "import_module", "module_name": import_path},
        )
        importlib.import_module(import_path)


def caller_module_name(prefix: str = "procrastinate") -> str:
    """
    Returns the module name of the first module of the stack that isn't under ``prefix``.
    If any problem occurs, raise `CallerModuleUnknown`.
    """

    try:
        frame = inspect.currentframe()
        while True:
            if not frame:
                raise ValueError("Empty frame")
            name = frame.f_globals["__name__"]  # May raise ValueError
            if not name.startswith(f"{prefix}."):
                break
            frame = frame.f_back
        return name
    except Exception as exc:
        raise exceptions.CallerModuleUnknown from exc


def async_to_sync(awaitable: Callable[..., Awaitable[T]], *args, **kwargs) -> T:
    """
    Given a callable returning an awaitable, call the callable, await it
    synchronously. Returns the result after it's done.
    """
    return sync.async_to_sync(awaitable)(*args, **kwargs)


async def sync_to_async(
    func: Callable[..., T], *args, **kwargs
) -> Callable[..., Awaitable[T]]:
    """
    Given a callable, return a callable that will call the original one in an
    async context.
    """
    return await sync.sync_to_async(func)(*args, **kwargs)


def causes(exc: BaseException | None):
    """
    From a single exception with a chain of causes and contexts, make an iterable
    going through every exception in the chain.
    """
    while exc:
        yield exc
        exc = exc.__cause__ or exc.__context__


def _get_module_name(obj: Any) -> str:
    module_name = obj.__module__
    if module_name != "__main__":
        return module_name

    module = inspect.getmodule(obj)
    # obj could be None, or has no __file__ if in an interactive shell
    # in which case, there's not a lot we can do.
    if not module or not getattr(module, "__file__", None):
        return module_name

    # We've checked this just above but mypy needs a direct proof
    assert module.__file__

    path = pathlib.Path(module.__file__)
    # If the path is absolute, it probably means __main__ is an executable from an
    # installed package
    if path.is_absolute():
        return module_name

    # Creating the dotted path from the path
    return ".".join([*path.parts[:-1], path.stem])


def get_full_path(obj: Any) -> str:
    try:
        name = obj.__name__
    except AttributeError as exc:
        raise exceptions.FunctionPathError(
            f"Couldn't extract a relevant task name for {obj}. Try passing `name=` to the task decorator"
        ) from exc
    return f"{_get_module_name(obj)}.{name}"


def utcnow() -> datetime.datetime:
    return datetime.datetime.now(tz=datetime.timezone.utc)


def parse_datetime(raw: str) -> datetime.datetime:
    try:
        # this parser is the stricter one, so we try it first
        dt = dateutil.parser.isoparse(raw)
        if not dt.tzinfo:
            dt = dt.replace(tzinfo=datetime.timezone.utc)
        return dt
    except ValueError:
        pass
    # this parser is quite forgiving, and will attempt to return
    # a value in most circumstances, so we use it as last option
    dt = dateutil.parser.parse(raw)
    dt = dt.replace(tzinfo=datetime.timezone.utc)
    return dt


class AwaitableContext(Generic[U]):
    """
    Provides an object that can be called this way:
    - value = await AppContext(...)
    - async with AppContext(...) as value: ...

    open_coro and close_coro are functions taking on arguments and returning coroutines.
    """

    def __init__(
        self,
        open_coro: Callable[[], Awaitable],
        close_coro: Callable[[], Awaitable],
        return_value: U,
    ):
        self._open_coro = open_coro
        self._close_coro = close_coro
        self._return_value = return_value

    async def __aenter__(self) -> U:
        await self._open_coro()
        return self._return_value

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._close_coro()

    def __await__(self):
        async def _inner_coro() -> U:
            await self._open_coro()
            return self._return_value

        return _inner_coro().__await__()


class EndMain(Exception):
    pass


@attr.dataclass()
class ExceptionRecord:
    task: asyncio.Task
    exc: Exception


async def run_tasks(
    main_coros: Iterable[Coroutine],
    side_coros: Iterable[Coroutine] | None = None,
    graceful_stop_callback: Callable[[], Any] | None = None,
):
    """
    Run multiple coroutines in parallel: the main coroutines and the side
    coroutines. Side coroutines are expected to run until they get cancelled.
    Main corountines are expected to return at some point. By default, this
    function will return None, but on certain circumstances, (see below) it can
    raise a `RunTaskError`. A callback `graceful_stop_callback` will be called
    if provided to ask the main coroutines to gracefully stop in case either
    one of them or one of the side coroutines raise.

    - If all coroutines from main_coros return and there is no exception in the
      coroutines from either `main_coros` or `side_coros`:
      - coroutines from `side_coros` are cancelled and awaited
      - the function return None

    - If any corountine from `main_coros` or `side_coros` raises an exception:
      - `graceful_stop_callback` is called (the idea is that it should ask
        coroutines from `main_coros` to exit gracefully)
      - the function then wait for main_coros to finish, registering any
        additional exception
      - coroutines from `side_coros` are cancelled and awaited, registering any
        additional exception
      - all exceptions from coroutines in both `main_coros` and `side_coros`
        are logged
      - the function raises `RunTaskError`

    It's not expected that coroutines from `side_coros` return. If this
    happens, the function will not react in a specific way.

    When a `RunTaskError` is raised because of one or more underlying
    exceptions, one exception is the `__cause__` (the first main or side
    coroutine that fails in the input iterables order, which will probably not
    the chronologically the first one to be raised). All exceptions are logged.
    """
    # Ensure all passed coros are futures (in our case, Tasks). This means that
    # all the coroutines start executing now.
    # `name` argument to create_task only exist on python 3.8+
    main_tasks = [asyncio.create_task(coro, name=coro.__name__) for coro in main_coros]
    side_tasks = [
        asyncio.create_task(coro, name=coro.__name__) for coro in side_coros or []
    ]
    for task in main_tasks + side_tasks:
        name = task.get_name()
        logger.debug(
            f"Started {name}",
            extra={
                "action": f"{name}_start",
            },
        )

    # Note that asyncio.gather() has 2 modes of execution:
    # - asyncio.gather(*aws)
    #     Interrupts the gather at the first exception, and raises this
    #     exception. Otherwise, return a list containing return values for all
    #     coroutines
    # - asyncio.gather(*aws, return_exceptions=True)
    #     Run every corouting until the end, return a list of either return
    #     values or raised exceptions (mixed).

    # The _main function will always raise: either an exception if one happens
    # in the main tasks, or EndMain if every coroutine returned
    async def _main():
        await asyncio.gather(*main_tasks)
        raise EndMain

    exception_records: list[ExceptionRecord] = []
    try:
        # side_tasks supposedly never finish, and _main always raises.
        # Consequently, it's theoretically impossible to leave this try block
        # without going through one of the except branches.
        await asyncio.gather(_main(), *side_tasks)
    except EndMain:
        pass
    except Exception as exc:
        logger.error(
            "Main coroutine error, initiating remaining coroutines stop. "
            f"Cause: {exc!r}",
            extra={
                "action": "run_tasks_stop_requested",
            },
        )
        if graceful_stop_callback:
            graceful_stop_callback()

        # Even if we asked the main tasks to stop, we still need to wait for
        # them to actually stop. This may take some time. At this point, any
        # additional exception will be registered but will not impact execution
        # flow.
        results = await asyncio.gather(*main_tasks, return_exceptions=True)
        for task, result in zip(main_tasks, results):
            if isinstance(result, Exception):
                exception_records.append(
                    ExceptionRecord(
                        task=task,
                        exc=result,
                    )
                )
            else:
                name = task.get_name()
                logger.debug(
                    f"{name} finished execution",
                    extra={
                        "action": f"{name}_stop",
                    },
                )

    for task in side_tasks:
        task.cancel()
        try:
            # task.cancel() says that the next time a task is executed, it will
            # raise, but we need to give control back to the task for it to
            # actually recieve the exception.
            await task
        except asyncio.CancelledError:
            name = task.get_name()
            logger.debug(
                f"Stopped {name}",
                extra={
                    "action": f"{name}_stop",
                },
            )
        except Exception as exc:
            exception_records.append(
                ExceptionRecord(
                    task=task,
                    exc=exc,
                )
            )

    for exception_record in exception_records:
        name = exception_record.task.get_name()
        message = f"{name} error: {exception_record.exc!r}"
        action = f"{name}_error"
        logger.exception(
            message,
            extra={
                "action": action,
            },
        )

    if exception_records:
        raise exceptions.RunTaskError from exception_records[0].exc


def add_namespace(name: str, namespace: str) -> str:
    return f"{namespace}:{name}" if namespace else name


def import_or_wrapper(*names: str) -> Iterable[types.ModuleType]:
    """
    Import given modules, or return a dummy wrapper that will raise an
    ImportError when used.
    """
    try:
        for name in names:
            yield importlib.import_module(name)
    except ImportError as exc:
        # In case psycopg is not installed, we'll raise an explicit error
        # only when the connector is used.
        exception = exc

        class Wrapper:
            def __getattr__(self, item):
                raise exception

        yield Wrapper()  # type: ignore


class MovedElsewhere:
    def __init__(self, name: str, new_location: str):
        self.name = name
        self.new_location = new_location

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        self.x

    def __getattr__(self, item):
        raise exceptions.MovedElsewhere(
            f"procrastinate.{self.name} has been moved to {self.new_location}"
        )


V = TypeVar("V")


async def gen_with_timeout(
    aiterable: AsyncIterator[V],
    timeout: float,
    raise_timeout: bool,
) -> AsyncGenerator[V, None]:
    """
    Wrap an async generator to add a timeout to each iteration.
    """
    aiterator = aiterable.__aiter__()
    while True:
        try:
            yield await asyncio.wait_for(aiterator.__anext__(), timeout=timeout)
        except StopAsyncIteration:
            break
        except asyncio.TimeoutError:
            if raise_timeout:
                raise
            else:
                return
