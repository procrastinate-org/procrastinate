import asyncio
import contextlib
import datetime
import json
import logging
import os
from typing import Any, Callable, Dict, Optional

import click

import procrastinate
from procrastinate import connector, exceptions, jobs, shell, types, utils, worker

logger = logging.getLogger(__name__)

PROGRAM_NAME = "procrastinate"
ENV_PREFIX = PROGRAM_NAME.upper()

CONTEXT_SETTINGS = {
    "help_option_names": ["-h", "--help"],
    "auto_envvar_prefix": ENV_PREFIX,
}


def get_log_level(verbosity: int) -> int:
    """
    Given the number of repetitions of the flag -v,
    returns the desired log level
    """
    return {0: logging.INFO, 1: logging.DEBUG}.get(min((1, verbosity)), 0)


def click_set_verbosity(ctx: click.Context, param: click.Parameter, value: int) -> int:
    set_verbosity(verbosity=value)
    return value


def set_verbosity(verbosity: int) -> None:
    level = get_log_level(verbosity=verbosity)
    logging.basicConfig(level=level)
    level_name = logging.getLevelName(level)
    logger.debug(
        f"Log level set to {level_name}",
        extra={"action": "set_log_level", "value": level_name},
    )


@contextlib.contextmanager
def handle_errors():
    try:
        yield
    except Exception as exc:
        logger.debug("Exception details:", exc_info=exc)
        messages = [str(e) for e in utils.causes(exc)]
        raise click.ClickException("\n".join(e for e in messages if e))


class MissingAppConnector(connector.BaseConnector):
    def close(self, *args, **kwargs):
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


@click.group(context_settings=CONTEXT_SETTINGS)
@click.pass_context
@click.option("--app", "-a", help="Dotted path to the Procrastinate app")
@click.option(
    "-v",
    "--verbose",
    is_eager=True,
    callback=click_set_verbosity,
    count=True,
    help="Use multiple times to increase verbosity",
)
@click.version_option(
    procrastinate.__version__, "-V", "--version", prog_name=PROGRAM_NAME
)
@handle_errors()
def cli(ctx: click.Context, app: str, **kwargs) -> None:
    """
    Interact with a Procrastinate app. See subcommands for details.

    All arguments can be passed by environment variables: PROCRASTINATE_UPPERCASE_NAME
    or PROCRASTINATE_COMMAND_UPPERCASE_NAME (examples: PROCRASTINATE_APP,
    PROCRASTINATE_DEFER_UNKNOWN, ...).
    """
    if app:
        app_obj = procrastinate.App.from_path(dotted_path=app)
    else:
        # If we don't provide an app, initialize a default one that will fail if it
        # needs a connector.
        app_obj = procrastinate.App(connector=MissingAppConnector())
    ctx.obj = app_obj

    worker_defaults = app_obj.worker_defaults.copy()
    worker_defaults["queues"] = ",".join(worker_defaults.get("queues") or [])
    ctx.default_map = {"worker": worker_defaults}


@cli.resultcallback()
@click.pass_obj
def close_connection(procrastinate_app: procrastinate.App, *args, **kwargs):
    # There's an internal click param named app, we can't name our variable "app" too.
    procrastinate_app.connector.close()

    asyncio.get_event_loop().close()


@cli.command("worker")
@click.pass_obj
@click.option("-n", "--name", default=worker.WORKER_NAME, help="Name of the worker")
@click.option(
    "-q",
    "--queues",
    default="",
    help="Comma-separated names of the queues to listen "
    "to (empty string for all queues)",
)
@click.option(
    "-c",
    "--concurrency",
    type=int,
    default=worker.WORKER_CONCURRENCY,
    help="Number of parallel asynchronous jobs to process at once",
)
@click.option(
    "-t",
    "--timeout",
    type=float,
    default=worker.WORKER_TIMEOUT,
    help="How long to wait for database event push before polling",
)
@click.option(
    "-w",
    "--wait/--one-shot",
    default=True,
    help="When all jobs have been processed, whether to "
    "terminate or to wait for new jobs",
)
@click.option(
    "-w",
    "--listen-notify/--no-listen-notify",
    default=True,
    help="Whether to actively listen for new jobs or periodically poll",
)
@handle_errors()
def worker_(app: procrastinate.App, queues: str, **kwargs):
    """
    Launch a worker, listening on the given queues (or all queues).
    Values default to App.worker_defaults and then App.run_worker() defaults values.
    """
    queue_list = [q.strip() for q in queues.split(",")] if queues else None
    if queue_list is None:
        queue_names = "all queues"
    else:
        queue_names = ", ".join(queue_list)
    click.echo(f"Launching a worker on {queue_names}")
    app.run_worker(queues=queue_list, **kwargs)  # type: ignore


@cli.command()
@click.pass_obj
@click.argument("task")
@click.argument("json_args", required=False)
@click.option(
    "--queue", help="The queue for deferring. Defaults to the task's default queue"
)
@click.option(
    "--lock", help="A lock string. Jobs sharing the same lock will not run concurrently"
)
@click.option(
    "--queueing-lock",
    help="A string value. The defer operation will fail if there already is a job "
    "waiting in the queue with the same queueing lock",
)
@click.option(
    "-i",
    "--ignore-already-enqueued/--no-ignore-already-enqueued",
    default=False,
    help="Exit with code 0 even if the queueing lock is already taken, while still "
    "displaying an error (default false)",
)
@click.option("--at", help="ISO-8601 localized datetime after which to launch the job")
@click.option(
    "--in", "in_", type=int, help="Number of seconds after which to launch the job"
)
@click.option(
    "--unknown/--no-unknown",
    help="Whether unknown tasks can be deferred (default false)",
)
@handle_errors()
def defer(
    app: procrastinate.App,
    task: str,
    json_args: str,
    lock: Optional[str],
    queueing_lock: Optional[str],
    ignore_already_enqueued: bool,
    queue: Optional[str],
    at: Optional[str],
    in_: Optional[int],
    unknown: bool,
):
    """
    Create a job from the given task, to be executed by a worker.
    TASK should be the name or dotted path to a task.
    JSON_ARGS should be a json object (a.k.a dictionary) with the job parameters
    """
    # Loading json args
    args = load_json_args(
        json_args=json_args, json_loads=app.connector.json_loads or json.loads
    )

    if at is not None and in_ is not None:
        raise click.UsageError("Cannot use both --at and --in")

    schedule_at = get_schedule_at(at=at)
    schedule_in = get_schedule_in(in_=in_)

    # Build kwargs. Remove all None kwargs to use their default values.
    configure_kwargs = {
        "lock": lock,
        "queueing_lock": queueing_lock,
        "schedule_at": schedule_at,
        "schedule_in": schedule_in,
        "queue": queue,
    }
    configure_kwargs = filter_none(configure_kwargs)

    # Configure the job. If the task is known, it will be used.
    job_deferrer = configure_job(
        app=app, task_name=task, configure_kwargs=configure_kwargs, unknown=unknown
    )

    # Printing info
    str_kwargs = ", ".join(f"{k}={repr(v)}" for k, v in args.items())
    click.echo(f"Launching a job: {task}({str_kwargs})")

    # And launching the job
    try:
        job_deferrer.defer(**args)  # type: ignore
    except exceptions.AlreadyEnqueued as exc:
        if not ignore_already_enqueued:
            raise
        click.echo(f"{exc} (ignored)")


def filter_none(dictionary: Dict) -> Dict:
    return {key: value for key, value in dictionary.items() if value is not None}


def load_json_args(json_args: str, json_loads: Callable) -> types.JSONDict:
    if json_args is None:
        return {}
    else:
        try:
            args = json_loads(json_args)
            assert type(args) == dict
        except Exception:
            raise click.BadArgumentUsage(
                "Incorrect JSON_ARGS value expecting a valid json object (or dict)"
            )
    return args


def get_schedule_at(at: Optional[str]) -> Optional[datetime.datetime]:
    if at is None:
        return None

    try:
        dt = utils.parse_datetime(at)
    except ValueError:
        raise click.BadOptionUsage("--at", f"Cannot parse datetime {at}")

    return dt


def get_schedule_in(in_: Optional[int]) -> Optional[Dict[str, int]]:
    if in_ is None:
        return None

    return {"seconds": in_}


def configure_job(
    app: procrastinate.App,
    task_name: str,
    configure_kwargs: Dict[str, Any],
    unknown: bool,
) -> jobs.JobDeferrer:
    app.perform_import_paths()
    try:
        return app.tasks[task_name].configure(**configure_kwargs)

    except KeyError:
        if unknown:
            return app.configure_task(name=task_name, **configure_kwargs)
        else:
            raise click.BadArgumentUsage(f"Task {task_name} not found.")


@cli.command()
@click.pass_obj
@click.option(
    "--apply",
    "action",
    flag_value="apply",
    help="Apply the schema to the DB (default)",
    default=True,
)
@click.option(
    "--read", "action", flag_value="read", help="Read the schema SQL and output it",
)
@click.option(
    "--migrations-path",
    "action",
    flag_value="migrations-path",
    help="Output the path to the directory containing the migration scripts",
)
@handle_errors()
def schema(app: procrastinate.App, action: str):
    """
    Apply SQL schema to the empty database. This won't work if the schema has already
    been applied.
    """
    schema_manager = app.schema_manager
    if action == "apply":
        click.echo("Applying schema")
        schema_manager.apply_schema()  # type: ignore
        click.echo("Done")
    elif action == "read":
        click.echo(schema_manager.get_schema(), nl=False)
    else:
        click.echo(schema_manager.get_migrations_path())


@cli.command()
@click.pass_obj
@handle_errors()
def healthchecks(app: procrastinate.App):
    """
    Check the state of procrastinate.
    """
    health_check = app.health_check_runner
    db_ok = health_check.check_connection()  # type: ignore
    if not db_ok:
        click.echo("Cannot connect to DB")
        return  # No need to go further
    click.echo("DB connection: OK")

    status_count = health_check.get_status_count()  # type: ignore
    for status, count in status_count.items():
        click.echo(f"{status.value}: {count}")


@cli.command("shell")
@click.pass_obj
@handle_errors()
def shell_(app: procrastinate.App):
    """
    Administration shell for procrastinate.
    """
    shell.ProcrastinateShell(app.admin).cmdloop()


def main():
    # https://click.palletsprojects.com/en/7.x/python3/
    os.environ.setdefault("LC_ALL", "C.UTF-8")
    os.environ.setdefault("LANG", "C.UTF-8")

    return cli()
