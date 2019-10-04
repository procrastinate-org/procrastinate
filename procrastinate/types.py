import typing as t

from typing_extensions import Protocol

JSONValue = t.Union[str, int, float, bool, None, t.Dict[str, t.Any], t.List[t.Any]]
JSONDict = t.Dict[str, JSONValue]


class SelectableObject(Protocol):
    def fileno(self) -> int:
        ...


Selectable = t.Union[int, SelectableObject]
