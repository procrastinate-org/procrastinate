import contextlib
import datetime
import json
import logging
import os
from typing import Any, Callable, Dict, Iterable, Optional

import click
import pendulum

import procrastinate
from procrastinate import connector, exceptions, jobs, types

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
    logger.info(
        f"Log level set to {level_name}",
        extra={"action": "set_log_level", "value": level_name},
    )


@contextlib.contextmanager
def handle_errors():
    try:
        yield
    except exceptions.ProcrastinateException as exc:
        raise click.ClickException(str(exc))
    except NotImplementedError:
        raise click.UsageError(
            "Missing app. This most probably happened because procrastinate needs an "
            "app via --app or the PROCRASTINATE_APP environment variable"
        )


def print_version(ctx, __, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo(f"{PROGRAM_NAME} {procrastinate.__version__}")
    click.echo(f"License: {procrastinate.__license__}")
    ctx.exit()


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
@click.option(
    "-V",
    "--version",
    is_flag=True,
    callback=print_version,
    expose_value=False,
    is_eager=True,
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
        ctx.obj = procrastinate.App.from_path(dotted_path=app)
    else:
        # If we don't provide an app, initialize a default one that will fail if it
        # needs its job store.
        ctx.obj = procrastinate.App(connector=connector.BaseConnector())


@cli.resultcallback()
@click.pass_obj
def close_connection(procrastinate_app: procrastinate.App, *args, **kwargs):
    # There's an internal click param named app, we can't name our variable "app" too.
    procrastinate_app.close_connection()  # type: ignore


@cli.command()
@click.pass_obj
@handle_errors()
@click.argument("queue", nargs=-1)
@click.option("--name", help="Name of the worker")
def worker(app: procrastinate.App, queue: Iterable[str], name: Optional[str]):
    """
    Launch a worker, listening on the given queues (or all queues).
    """
    queues = list(queue) or None
    queue_names = ", ".join(queues) if queues else "all queues"
    click.echo(f"Launching a worker on {queue_names}")
    app.run_worker(queues=queues, name=name)  # type: ignore


@cli.command()
@click.pass_obj
@handle_errors()
@click.argument("task")
@click.argument("json_args", required=False)
@click.option(
    "--lock", help="A lock string. Jobs sharing the same lock will not run concurrently"
)
@click.option("--queue", help="The queue for deferring. Defaults to the task ")
@click.option("--at", help="ISO-8601 localized datetime after which to launch the job")
@click.option(
    "--in", "in_", type=int, help="Number of seconds after which to launch the job"
)
@click.option(
    "--unknown/--no-unknown",
    help="Whether unknown tasks can be deferred (default false)",
)
def defer(
    app: procrastinate.App,
    task: str,
    json_args: str,
    lock: Optional[str],
    queue: Optional[str],
    at: Optional[str],
    in_: Optional[int],
    unknown: bool,
):
    """
    Create a job from the given task, to be executed by a worker.
    TASK should be the name or dotted path to a task.
    JSON_ARGS should be a json object (a.k.a dictionnary) with the job parameters
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
    job_deferrer.defer(**args)  # type: ignore


def filter_none(dictionnary: Dict) -> Dict:
    return {key: value for key, value in dictionnary.items() if value is not None}


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
        return pendulum.parse(at)
    except pendulum.exceptions.ParserError:
        raise click.BadOptionUsage("--at", f"Cannot parse datetime {at}")


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
@handle_errors()
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


def main():
    # https://click.palletsprojects.com/en/7.x/python3/
    os.environ.setdefault("LC_ALL", "C.UTF-8")
    os.environ.setdefault("LANG", "C.UTF-8")

    return cli()
