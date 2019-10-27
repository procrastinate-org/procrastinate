import asyncio
import functools
import importlib
import logging
from typing import Awaitable, Iterable, Type, TypeVar

from procrastinate import exceptions

T = TypeVar("T")

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
        wrap_one(cls=cls, attribute_name=attribute_name)

    return cls


def wrap_one(cls: Type, attribute_name: str):
    suffix = "_async"
    if attribute_name.startswith("_") or not attribute_name.endswith(suffix):
        return

    attribute = getattr(cls, attribute_name)

    # Keep only async def methods
    if not asyncio.iscoroutinefunction(attribute):
        return

    # Create a wrapper that will call the method in a run_until_complete
    @functools.wraps(attribute)
    def wrapper(self, *args, **kwargs):
        awaitable = attribute(self, *args, **kwargs)
        return sync_await(awaitable=awaitable)

    # Save this new method on the class
    name = wrapper.__name__ = attribute_name[: -len(suffix)]
    setattr(cls, name, wrapper)


def sync_await(awaitable: Awaitable[T]) -> T:
    """
    Given an awaitable, awaits it synchronously. Returns the result after it's done.
    """
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(awaitable)
