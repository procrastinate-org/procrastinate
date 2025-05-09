from __future__ import annotations

import datetime
import typing as t

from typing_extensions import NotRequired

JSONValue = t.Union[str, int, float, bool, None, dict[str, t.Any], list[t.Any]]
JSONDict = dict[str, JSONValue]


class TimeDeltaParams(t.TypedDict):
    weeks: NotRequired[int]
    days: NotRequired[int]
    hours: NotRequired[int]
    minutes: NotRequired[int]
    seconds: NotRequired[int]
    milliseconds: NotRequired[int]
    microseconds: NotRequired[int]


class JobToDefer(t.NamedTuple):
    queue_name: str
    task_name: str
    priority: int
    lock: str | None
    queueing_lock: str | None
    args: JSONDict
    scheduled_at: datetime.datetime | None
