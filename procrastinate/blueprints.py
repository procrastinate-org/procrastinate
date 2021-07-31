import functools
from typing import TYPE_CHECKING, Any, Callable, List, Optional

from procrastinate import jobs, protocols, retry

if TYPE_CHECKING:
    from procrastinate import app, tasks


class Blueprint(protocols.TaskCreator):
    """
    A Blueprint provides a way to declare tasks that can be registered on an
    `App` later::

        bp = Blueprint()

        ... declare tasks ...

        app.register(bp)

    Notes
    -----
    Deffering a blueprint task before the it is bound to an app will raise an
    UnboundTaskError::

        bp = Blueprint()

        @bp.task
        def my_task():
            ...

        my_task.defer()

        >> AssertionError: Tried to configure task whilst self.app was None



    """

    def __init__(self):
        self.tasks = {}

    def _register_task(self, task: "tasks.Task") -> None:
        self.tasks[task.name] = task

    def register(self, app: "app.App") -> None:
        for task in self.tasks.values():
            task.app = app
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
        """
        Like :meth:`App.task <procrastinate.App.task>` except tasks **are not** bound to
        an app until the blueprint is registered on an app.

        Declare a function as a task as you normally would::

            @bp.task(...)
            def my_task(args):
                ...

        Un-configured task decorator will use default values for all parameters::

            @bp.task
            def my_task(args):
                ...


        Parameters
        ----------
        _func :
            The decorated function
        queue :
            The name of the queue in which jobs from this task will be launched, if
            the queue is not overridden at launch.
            Default is ``"default"``.
            When a worker is launched, it can listen to specific queues, or to all
            queues.
        lock :
            Default value for the ``lock`` (see `Task.defer`).
        queueing_lock:
            Default value for the ``queueing_lock`` (see `Task.defer`).
        name :
            Name of the task, by default the full dotted path to the decorated function.
            if the function is nested or dynamically defined, it is important to give
            it a unique name, and to make sure the module that defines this function
            is listed in the ``import_paths`` of the `procrastinate.App`.
        aliases:
            Additional names for the task.
            The main use case is to gracefully rename tasks by moving the old
            name to aliases (these tasks can have been scheduled in a distant
            future, so the aliases can remain for a long time).
        retry :
            Details how to auto-retry the task if it fails. Can be:

            - A ``boolean``: will either not retry or retry indefinitely
            - An ``int``: the number of retries before it gives up
            - A `procrastinate.RetryStrategy` instance for complex cases

            Default is no retry.
        pass_context :
            Passes the task execution context in the task as first
        """

        def _wrap(func: Callable[..., "tasks.Task"]):
            from procrastinate import tasks

            task = tasks.Task(
                func,
                app=None,
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
