import asyncio
import functools
import json
import logging
import sys
from typing import Any, Callable, Dict, List, Optional, Union

import configargparse as argparse
from asgiref import sync

if sys.version_info < (3, 8):
    from typing_extensions import Literal
else:
    from typing import Literal

import procrastinate
from procrastinate import connector, exceptions, jobs, shell, types, utils, worker

logger = logging.getLogger(__name__)

PROGRAM_NAME = "procrastinate"
ENV_PREFIX = PROGRAM_NAME.upper()


def get_log_level(verbosity: int) -> int:
    """
    Given the number of repetitions of the flag -v,
    returns the desired log level
    """
    return {0: logging.INFO, 1: logging.DEBUG}.get(min((1, verbosity)), 0)


Style = Union[Literal["%"], Literal["{"], Literal["$"]]


def configure_logging(verbosity: int, format: str, style: Style) -> None:
    level = get_log_level(verbosity=verbosity)
    logging.basicConfig(level=level, format=format, style=style)
    level_name = logging.getLevelName(level)
    logger.debug(
        f"Log level set to {level_name}",
        extra={"action": "set_log_level", "value": level_name},
    )


def print_stderr(*args):
    print(*args, file=sys.stderr)


class MissingAppConnector(connector.BaseAsyncConnector):
    def open(self, *args, **kwargs):
        pass

    def close(self, *args, **kwargs):
        pass

    async def open_async(self, *args, **kwargs):
        pass

    async def close_async(self, *args, **kwargs):
        pass

    def execute_query(self, *args, **kwargs):
        raise exceptions.MissingApp

    def execute_query_one(self, *args, **kwargs):
        raise exceptions.MissingApp

    def execute_query_all(self, *args, **kwargs):
        raise exceptions.MissingApp

    async def execute_query_async(self, *args, **kwargs):
        raise exceptions.MissingApp

    async def execute_query_one_async(self, *args, **kwargs):
        raise exceptions.MissingApp

    async def execute_query_all_async(self, *args, **kwargs):
        raise exceptions.MissingApp

    async def listen_notify(self, *args, **kwargs):
        raise exceptions.MissingApp


class ActionWithNegative(argparse.argparse._StoreTrueAction):
    def __init__(self, *args, negative: Optional[str], **kwargs):
        super().__init__(*args, **kwargs)
        self.negative = negative

    def __call__(self, parser, ns, values, option):
        if self.negative is None:
            setattr(ns, self.dest, not option.startswith("--no-"))
            return
        setattr(ns, self.dest, option != self.negative)


def store_true_with_negative(negative: Optional[str] = None):
    """
    Return an argparse action that works like store_true but also accepts
    a flag to set the value to False. By default, any flag starting with
    `--no-` will set the value to False. If a string is provided as the
    `negative` argument, this flags will set the value to False.
    """
    return functools.partial(ActionWithNegative, negative=negative)


def load_app(app_path: str) -> procrastinate.App:
    if app_path == "":
        # If we don't provide an app, initialize a default one that will fail if it
        # needs a connector.
        return procrastinate.App(connector=MissingAppConnector())

    try:
        app = procrastinate.App.from_path(dotted_path=app_path)
    except exceptions.LoadFromPathError as exc:
        raise argparse.ArgumentError(
            None, f"Could not load app from {app_path}"
        ) from exc
    if not isinstance(app.connector, connector.BaseAsyncConnector):
        raise argparse.ArgumentError(
            None,
            "The connector provided by the app is not async. "
            "Please use an async connector for the procrastinate CLI.",
        )
    return app


def cast_queues(queues: str) -> Optional[List[str]]:
    cleaned_queues = (queue.strip() for queue in queues.split(","))
    return [queue for queue in cleaned_queues if queue] or None


def get_parser() -> argparse.ArgumentParser:
    # Important note: the FIRST long option is the one used for the
    # variable name BUT when an envvar is use, configargparse will substitute
    # it for the LAST option. This means in case of store_true_with_negative,
    # we need to repeat the positive option as both the first long option AND
    # the last option. This sucks.
    parser = argparse.ArgumentParser(
        prog=PROGRAM_NAME,
        description="Interact with a Procrastinate app. See subcommands for details.",
        add_env_var_help=True,
        auto_env_var_prefix=f"{ENV_PREFIX}_",
    )
    parser.add_argument(
        "-a",
        "--app",
        default="",
        type=load_app,
        help="Dotted path to the Procrastinate app",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        default=0,
        action="count",
        help="Use multiple times to increase verbosity",
    )
    log_group = parser.add_argument_group("Logging")
    log_group.add_argument(
        "--log-format",
        default=logging.BASIC_FORMAT,
        help="Defines the format used for logging (see "
        "https://docs.python.org/3/library/logging.html#logrecord-attributes)",
    )
    log_group.add_argument(
        "--log-format-style",
        default="%",
        choices=["%", "{", "$"],
        help="Defines the style for the log format string (see "
        "https://docs.python.org/3/howto/logging-cookbook.html#use-of-alternative-formatting-styles)",
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s, version {procrastinate.__version__}",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    worker_parser = subparsers.add_parser(
        "worker",
        help="Launch a worker, listening on the given queues (or all queues). "
        "Values default to App.worker_defaults and then App.run_worker() defaults values.",
        add_env_var_help=True,
        auto_env_var_prefix=f"{ENV_PREFIX}_WORKER_",
        argument_default=argparse.SUPPRESS,
    )
    worker_parser.set_defaults(func=worker_)
    worker_parser.add_argument(
        "-n",
        "--name",
        help="Name of the worker",
    )
    worker_parser.add_argument(
        "-q",
        "--queues",
        type=cast_queues,
        help="Comma-separated names of the queues to listen "
        "to (empty string for all queues)",
    )
    worker_parser.add_argument(
        "-c",
        "--concurrency",
        type=int,
        help="Number of parallel asynchronous jobs to process at once",
    )
    worker_parser.add_argument(
        "-t",
        "--timeout",
        type=float,
        help="How long to wait for database event push before polling",
    )
    worker_parser.add_argument(
        "-w",
        "--wait",
        "--one-shot",
        # See note at the top.
        "--wait",
        action=store_true_with_negative("--one-shot"),
        help="When all jobs have been processed, whether to "
        "terminate or to wait for new jobs",
    )
    worker_parser.add_argument(
        "-l",
        "--listen-notify",
        "--no-listen-notify",
        # See note at the top.
        "--listen-notify",
        action=store_true_with_negative(),
        help="Whether to actively listen for new jobs or periodically poll",
    )
    worker_parser.add_argument(
        "--delete-jobs",
        choices=worker.DeleteJobCondition,
        type=worker.DeleteJobCondition,
        help="Whether to delete jobs on completion",
    )

    defer_parser = subparsers.add_parser(
        "defer",
        help="Create a job from the given task, to be executed by a worker. "
        "TASK should be the name or dotted path to a task. "
        "JSON_ARGS should be a json object (a.k.a dictionary) with the job parameters",
        add_env_var_help=True,
        auto_env_var_prefix=f"{ENV_PREFIX}_DEFER_",
    )
    defer_parser.set_defaults(func=defer)
    defer_parser.add_argument(
        "task",
        help="Name or dotted path to the task to defer",
    )
    defer_parser.add_argument(
        "json_args",
        nargs="?",
        # We can't cast it right away into json, because we need to use
        # the app's json loads function.
        help="JSON object with the job parameters",
    )
    defer_parser.add_argument(
        "--queue",
        default=argparse.SUPPRESS,
        help="The queue for deferring. Defaults to the task's default queue",
    )
    defer_parser.add_argument(
        "--lock",
        default=argparse.SUPPRESS,
        help="A lock string. Jobs sharing the same lock will not run concurrently",
    )
    defer_parser.add_argument(
        "--queueing-lock",
        default=argparse.SUPPRESS,
        help="A string value. The defer operation will fail if there already is a job "
        "waiting in the queue with the same queueing lock",
    )
    defer_parser.add_argument(
        "-i",
        "--ignore-already-enqueued",
        "--no-ignore-already-enqueued",
        # See note at the top.
        "--ignore-already-enqueued",
        action=store_true_with_negative(),
        help="Exit with code 0 even if the queueing lock is already taken, while still "
        "displaying an error (default false)",
    )
    time_group = defer_parser.add_mutually_exclusive_group()
    time_group.add_argument(
        "--at",
        default=argparse.SUPPRESS,
        type=utils.parse_datetime,
        help="ISO-8601 localized datetime after which to launch the job",
    )
    time_group.add_argument(
        "--in",
        default=argparse.SUPPRESS,
        dest="in_",
        type=lambda s: {"seconds": int(s)},
        help="Number of seconds after which to launch the job",
    )
    defer_parser.add_argument(
        "--unknown",
        "--no-unknown",
        # See note at the top.
        "--unknown",
        action=store_true_with_negative(),
        help="Whether unknown tasks can be deferred (default false)",
    )

    schema_parser = subparsers.add_parser(
        "schema",
        help="Apply SQL schema to the empty database. This won't work if the schema has already "
        "been applied.",
        add_env_var_help=True,
        auto_env_var_prefix=f"{ENV_PREFIX}_SCHEMA_",
    )
    schema_parser.set_defaults(func=schema)
    schema_parser.add_argument(
        "--apply",
        action="store_const",
        const="apply",
        dest="action",
        help="Apply the schema to the DB (default)",
    )
    schema_parser.add_argument(
        "--read",
        action="store_const",
        const="read",
        dest="action",
        help="Read the schema SQL and output it",
    )
    schema_parser.add_argument(
        "--migrations-path",
        action="store_const",
        const="migrations_path",
        dest="action",
        help="Output the path to the directory containing the migration scripts",
    )

    healthchecks_parser = subparsers.add_parser(
        "healthchecks",
        help="Check the state of procrastinate",
        add_env_var_help=True,
        auto_env_var_prefix=f"{ENV_PREFIX}_HEALTHCHECKS_",
    )
    healthchecks_parser.set_defaults(func=healthchecks)

    shell_parser = subparsers.add_parser(
        "shell",
        help="Administration shell for procrastinate",
        add_env_var_help=True,
        auto_env_var_prefix=f"{ENV_PREFIX}_SHELL_",
    )
    shell_parser.set_defaults(func=shell_)

    return parser


async def cli(args):
    parser = get_parser()
    parsed = vars(parser.parse_args(args))

    configure_logging(
        verbosity=parsed.pop("verbose"),
        format=parsed.pop("log_format"),
        style=parsed.pop("log_format_style"),
    )
    parsed.pop("command")
    try:
        async with parsed.pop("app").open_async() as app:
            # Before calling the subcommand function,
            # we want to have popped all top-level arguments
            # from the parsed dict and kept only the subcommand
            # arguments.
            await parsed.pop("func")(app=app, **parsed)
    except Exception as exc:
        logger.debug("Exception details:", exc_info=exc)
        messages = [str(e) for e in utils.causes(exc)]
        exit_message = "\n".join(e.strip() for e in messages[::-1] if e)
        print_stderr(exit_message)
        sys.exit(1)


async def worker_(
    app: procrastinate.App,
    **kwargs,
):
    """
    Launch a worker, listening on the given queues (or all queues).
    Values default to App.worker_defaults and then App.run_worker() defaults values.
    """
    queues = kwargs.get("queues")
    print_stderr(
        f"Launching a worker on {'all queues' if not queues else ', '.join(queues)}"
    )
    await app.run_worker_async(**kwargs)


async def defer(
    app: procrastinate.App,
    task: str,
    json_args: Optional[str],
    ignore_already_enqueued: bool,
    unknown: bool,
    **configure_kwargs,
):
    """
    Create a job from the given task, to be executed by a worker.
    TASK should be the name or dotted path to a task.
    JSON_ARGS should be a json object (a.k.a dictionary) with the job parameters
    """
    # Loading json args
    args = (
        load_json_args(
            json_args=json_args, json_loads=app.connector.json_loads or json.loads
        )
        if json_args
        else {}
    )
    # Configure the job. If the task is known, it will be used.
    job_deferrer = configure_task(
        app=app,
        task_name=task,
        configure_kwargs=configure_kwargs,
        allow_unknown=unknown,
    )

    # Printing info
    str_kwargs = ", ".join(f"{k}={repr(v)}" for k, v in args.items())
    print_stderr(f"Launching a job: {task}({str_kwargs})")
    # And launching the job
    try:
        await job_deferrer.defer_async(**args)  # type: ignore
    except exceptions.AlreadyEnqueued as exc:
        if not ignore_already_enqueued:
            raise
        print_stderr(f"{exc} (ignored)")


def load_json_args(json_args: str, json_loads: Callable) -> types.JSONDict:
    if json_args is None:
        return {}
    else:
        try:
            args = json_loads(json_args)
            assert isinstance(args, dict)
        except Exception as exc:
            raise ValueError(
                "Incorrect JSON_ARGS value expecting a valid json object (or dict)"
            ) from exc
    return args


def configure_task(
    app: procrastinate.App,
    task_name: str,
    configure_kwargs: Dict[str, Any],
    allow_unknown: bool,
) -> jobs.JobDeferrer:
    return app.configure_task(
        name=task_name, allow_unknown=allow_unknown, **configure_kwargs
    )


async def schema(app: procrastinate.App, action: str):
    """
    Apply SQL schema to the empty database. This won't work if the schema has already
    been applied.
    """
    action = action or "apply"
    schema_manager = app.schema_manager
    if action == "apply":
        print_stderr("Applying schema")
        await schema_manager.apply_schema_async()
        print_stderr("Done")
    elif action == "read":
        print(schema_manager.get_schema().strip())
    else:
        print(schema_manager.get_migrations_path())


async def healthchecks(app: procrastinate.App):
    """
    Check the state of procrastinate.
    """
    db_ok = await app.check_connection_async()
    # If app or DB is not configured correctly, we raise before this point
    print("App configuration: OK")
    print("DB connection: OK")

    if not db_ok:
        raise RuntimeError(
            "Connection to the database works but the procrastinate_jobs table was not "
            "found. Have you applied database migrations (see "
            "`procrastinate schema -h`)?"
        )

    print("Found procrastinate_jobs table: OK")


async def shell_(app: procrastinate.App):
    """
    Administration shell for procrastinate.
    """
    shell_obj = shell.ProcrastinateShell(
        job_manager=app.job_manager,
    )

    await sync.sync_to_async(shell_obj.cmdloop)()


def main():
    asyncio.run(cli(sys.argv[1:]))
