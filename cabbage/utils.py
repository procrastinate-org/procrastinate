import importlib
from typing import Any


def load_from_path(path: str) -> Any:
    """
    Import and return then object at the given full python path.
    """
    if "." not in path:
        raise ImportError(f"{path} is not a valid path")
    path, name = path.rsplit(".", 1)
    module = importlib.import_module(path)

    try:
        imported = getattr(module, name)
    except AttributeError as exc:
        raise ImportError from exc

    return imported
