from enum import Enum
from typing import NamedTuple

from cabbage import types


class Status(Enum):
    TODO = "todo"
    DOING = "doing"
    DONE = "done"
    ERROR = "error"


class Job(NamedTuple):
    id: int
    task_name: str
    queue: str
    kwargs: types.JSONDict
    lock: str
