import asyncio
import contextlib
import datetime
import functools
import importlib
import inspect
import logging
import pathlib
import types
from typing import Any, Awaitable, Callable, Iterable, Optional, Type, TypeVar

import dateutil.parser

from procrastinate import exceptions

T = TypeVar("T")
U = TypeVar("U")

logger = logging.getLogger(__name__)


def load_from_path(path: str, allowed_type: Type[T]) -> T:
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

    if not isinstance(imported, allowed_type):
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


def add_sync_api(cls: Type) -> Type:
    """
    Applying this decorator to a class with async methods named "<name>_async"
    will create a sync version named "<name>" of these methods that performs the same
    thing but synchronously.
    """
    # Iterate on all class attributes
    for attribute_name in dir(cls):
        add_method_sync_api(cls=cls, method_name=attribute_name)

    return cls


# https://github.com/sphinx-doc/sphinx/issues/7559
SYNC_ADDENDUM = """

        This method is the synchronous counterpart of `{}`.
        Because of a slight issue in automatic doc generation, it
        is shown here as "async", but this function is synchronous.
"""

ASYNC_ADDENDUM = """

        This method is the asynchronous counterpart of `{}`.
"""


def add_method_sync_api(*, cls: Type, method_name: str, suffix: str = "_async"):
    if method_name.startswith("_") or not method_name.endswith(suffix):
        return

    attribute, function = get_raw_method(cls=cls, method_name=method_name)

    # Keep only async def methods
    if not asyncio.iscoroutinefunction(function):
        return

    if isinstance(attribute, types.FunctionType):  # classic method
        method_type = "method"
    elif isinstance(attribute, classmethod):
        method_type = "classmethod"
    elif isinstance(attribute, staticmethod):
        method_type = "staticmethod"
    else:
        raise ValueError(f"Invalid object of type {type(attribute)}")

    attribute.__doc__ = attribute.__doc__ or ""

    # Create a wrapper that will call the method in a run_until_complete
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        if method_type == "method":
            final_class = type(args[0])
        elif method_type == "classmethod":
            final_class = args[0]
        else:
            final_class = cls

        _, function = get_raw_method(cls=final_class, method_name=method_name)

        awaitable = function(*args, **kwargs)
        return sync_await(awaitable=awaitable)

    sync_name = method_name[: -len(suffix)]
    attribute.__doc__ += ASYNC_ADDENDUM.format(sync_name)

    final_wrapper: Any
    if method_type == "method":
        final_wrapper = wrapper
    elif method_type == "classmethod":
        final_wrapper = classmethod(wrapper)
    else:
        final_wrapper = staticmethod(wrapper)

    # Save this new method on the class
    wrapper.__name__ = sync_name
    final_wrapper.__doc__ += SYNC_ADDENDUM.format(method_name)
    setattr(cls, sync_name, final_wrapper)


def get_raw_method(cls: Type, method_name: str):
    """
    Extract a method from the class, without triggering the descriptor.
    Return 2 objects:

    - the method itself stored on the class (which may be a function, a classmethod or
      a staticmethod)
    - The real function underneath (the same function as above for a normal method,
      and the wrapped function for static and class methods).

    """
    # Methods are descriptors so using getattr here will not give us the real method
    cls_vars = vars(cls)
    method = cls_vars[method_name]

    # If method is a classmethod or staticmethod, its real function, that may be
    # async, is stored in __func__.
    wrapped = getattr(method, "__func__", method)

    return method, wrapped


def sync_await(awaitable: Awaitable[T]) -> T:
    """
    Given an awaitable, awaits it synchronously. Returns the result after it's done.
    """

    loop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(awaitable)


def causes(exc: Optional[BaseException]):
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
    if not module or not hasattr(module, "__file__"):
        return module_name

    path = pathlib.Path(module.__file__)
    # If the path is absolute, it probably means __main__ is an executable from an
    # installed package
    if path.is_absolute():
        return module_name

    # Creating the dotted path from the path
    return ".".join([*path.parts[:-1], path.stem])


def get_full_path(obj: Any) -> str:

    return f"{_get_module_name(obj)}.{obj.__name__}"


@contextlib.contextmanager
def task_context(awaitable: Awaitable, name: str):
    """
    Take an awaitable, return a context manager.

    On enter, launch the awaitable as a task that will execute in parallel in the
    event loop. On exit, cancel the task (and log). If the task ends with an exception
    log it.

    A name is required for logging purposes.
    """
    nice_name = name.replace("_", " ").title()

    async def wrapper():
        try:
            logger.debug(f"Started {nice_name}", extra={"action": f"{name}_start"})
            await awaitable
        except asyncio.CancelledError:
            logger.debug(f"Stopped {nice_name}", extra={"action": f"{name}_stop"})
            raise

        except Exception:
            logger.exception(f"{nice_name} error", extra={"action": f"{name}_error"})

    try:
        task = asyncio.ensure_future(wrapper())
        yield task
    finally:
        task.cancel()


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


class AwaitableContext:
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
