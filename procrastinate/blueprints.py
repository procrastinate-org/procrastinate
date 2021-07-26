import functools
from typing import TYPE_CHECKING, Any, Callable, List, Optional

from procrastinate import jobs, retry

if TYPE_CHECKING:
    from procrastinate import app, tasks


class BluePrint:
    def __init__(self):
        self.tasks = {}

    def _register_task(self, task: "tasks.Task") -> None:
        self.tasks[task.name] = task

    def register(self, app: "app.App") -> None:
        for task in self.tasks.values():
            app._register(task)

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
        def _wrap(func: Callable[..., "tasks.Task"]):
            from procrastinate import tasks

            task = tasks.Task(
                func,
                app=self,
                queue=queue,
                lock=lock,
                queueing_lock=queueing_lock,
                name=name,
                aliases=aliases,
                retry=retry,
                pass_context=pass_context,
            )
            self._register_task(task)

            return functools.update_wrapper(task, func, updated=())

        if _func is None:  # Called as @app.task(...)
            return _wrap

        return _wrap(_func)  # Called as @app.task
