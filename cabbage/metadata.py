from typing import Callable, Iterable, Mapping, Type, Union

import importlib_metadata
from typing_extensions import Protocol


def extract_metadata() -> Mapping[str, str]:

    # Backport of Python 3.8's future importlib.metadata()
    metadata = importlib_metadata.metadata("cabbage")

    return {
        "author": metadata["Author"],
        "email": metadata["Author-email"],
        "copyright": metadata["License"],
        "url": metadata["Home-page"],
        "version": metadata["Version"],
    }


class EntryPoint(Protocol):
    name: str
    value: str

    # This is a white lie: it could be anything,
    # but we'll assume entry points are always on classes.
    def load(self) -> Type:
        ...


def entrypoints(name) -> Iterable[EntryPoint]:
    return importlib_metadata.entry_points()[name]
