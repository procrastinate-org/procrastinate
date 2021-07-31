import functools
import logging
import sys
from typing import TYPE_CHECKING, Any, Callable, List, Optional

from procrastinate import exceptions, jobs, retry, utils

if TYPE_CHECKING:
    from procrastinate import app, tasks
logger = logging.getLogger(__name__)


class Blueprint:
    """
    A Blueprint provides a way to declare tasks that can be registered on an
    `App` later::

        # Create blueprint for all tasks related to the cat
        cat_blueprint = Blueprint()

        # Declare tasks
        @cat_blueprint.task(lock="...")
        def feed_cat():
            ...

        # Register blueprint (will register ``cat:path.to.feed_cat``)
        app.add_tasks_from(cat_blueprint, namespace="cat")

    A blueprint can add tasks from another blueprint::

        blueprint_a, blueprint_b = Blueprint(), Blueprint()

        @blueprint_b.task(lock="...")
        def my_task():
            ...

        blueprint_a.add_tasks_from(blueprint_b, namespace="b")

        # Registers task "a:b:path.to.my_task"
        app.add_tasks_from(blueprint_a, namespace="a")

    Raises
    ------
    TaskNotRegistered:
        Calling a blueprint task before the it is bound to an `App` will raise a
        `TaskNotRegistered` error::

            blueprint = Blueprint()

            # Declare tasks
            @blueprint.task
            def my_task():
                ...

            >>> my_task.defer()

            Traceback (most recent call last):
                File "..."
            `TaskNotRegistered`: ...
    """

    def __init__(self):
        self.tasks: Dict[str, "tasks.Task"] = {}
        self._check_stack()

    def _check_stack(self):
        # Emit a warning if the app is defined in the __main__ module
        try:
            name = utils.caller_module_name()
        except exceptions.CallerModuleUnknown:
            logger.warning(
                "Unable to determine where the app was defined. "
                "See https://procrastinate.readthedocs.io/en/stable/discussions.html#top-level-app .",
                extra={"action": "app_location_unknown"},
                exc_info=True,
            )

        if name == "__main__":
            logger.warning(
                f"{type(self).__name__} is instantiated in the main Python module "
                f"({sys.argv[0]}). "
                "See https://procrastinate.readthedocs.io/en/stable/discussions.html#top-level-app .",
                extra={"action": "app_defined_in___main__"},
                exc_info=True,
            )

    def _register_task(self, task: "tasks.Task") -> None:
        to_add = {}
        if task.name in self.tasks:
            raise exceptions.TaskAlreadyRegistered(
                f"A task called {task.name} was already registered."
            )
        to_add[task.name] = task

        for alias in task.aliases:
            if alias in self.tasks:
                raise exceptions.TaskAlreadyRegistered(
                    f"A task with alias {alias} was already registered"
                )

            to_add[alias] = task

        self.tasks.update(to_add)

    def register(self, app: "app.App") -> None:
        for task in self.tasks.values():
            task.app = app
            app._register_task(task)

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
        Declare a function as a task. This method is meant to be used as a decorator::

            @app.task(...)
            def my_task(args):
                ...

        or::

            @app.task
            def my_task(args):
                ...

        The second form will use the default value for all parameters.

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
