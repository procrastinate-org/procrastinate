from typing import Any, Callable, List, Optional, Protocol

from procrastinate import retry


class TaskCreator(Protocol):
    def task(
        self,
        _func: Optional[Callable],
        *,
        name: Optional[str],
        aliases: Optional[List[str]],
        retry: retry.RetryValue,
        pass_context: bool,
        queue: str,
        lock: Optional[str],
        queueing_lock: Optional[str],
    ) -> Any:
        ...
