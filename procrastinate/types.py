import typing as t

from typing_extensions import Protocol

JSONValue = t.Union[str, int, float, bool, None, t.Dict[str, t.Any], t.List[t.Any]]
JSONDict = t.Dict[str, JSONValue]


class Cursor(Protocol):
    def __enter__(self) -> "Cursor":
        ...

    def __exit__(self, type, value, traceback):
        ...

    def execute(self, query: str, *args):
        ...


class Connection(Protocol):
    def __enter__(self) -> "Connection":
        ...

    def __exit__(self, type, value, traceback):
        ...

    def close(self):
        ...

    def cursor(self) -> Cursor:
        ...
