from typing import Mapping, Iterable, Callable
from typing_extensions import Protocol

import importlib_metadata


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


class Loadable(Protocol):
    def load(self) -> Callable:
        ...


def entrypoints(name) -> Iterable[Loadable]:

    return importlib_metadata.entry_points()[name]
