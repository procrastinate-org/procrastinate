from typing import Any, Callable, List, Optional

from typing_extensions import Protocol

from procrastinate import jobs, retry


class TaskCreator(Protocol):
    def task(
        self,
        _func: Optional[Callable] = None,
        *,
        name: Optional[str] = None,
        aliases: Optional[List[str]] = None,
        retry: retry.RetryValue = False,
        pass_context: bool = False,
        queue: str = jobs.DEFAULT_QUEUE,
        lock: Optional[str] = None,
        queueing_lock: Optional[str] = None,
    ) -> Any:
        ...
