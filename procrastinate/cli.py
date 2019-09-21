import contextlib
import datetime
import json
import logging
import os
from typing import Dict, Iterable, Optional

import click
import pendulum

import procrastinate
from procrastinate import exceptions, tasks, types

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
    logger.debug(
        "Log level set",
        extra={"action": "set_log_level", "value": logging.getLevelName(level)},
    )


@contextlib.contextmanager
def handle_errors():
    try:
        yield
    except exceptions.ProcrastinateException as exc:
        raise click.ClickException(str(exc))


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

    All arguments can be passed by environment variables: PROCRASTINATE_UPPERCASE_NAME.
    """
    if app:
        ctx.obj = procrastinate.App.from_path(dotted_path=app)
    else:
        # If we don't provide an app, initialize a default one that will fail if it
        # needs its job store.
        ctx.obj = procrastinate.App(job_store=procrastinate.BaseJobStore())


@cli.command()
@click.pass_obj
@handle_errors()
@click.argument("queue", nargs=-1)
def worker(app: procrastinate.App, queue: Iterable[str]):
    """
    Launch a worker, listening on the given queues (or all queues).
    """
    queues = list(queue) or None
    queue_names = ", ".join(queues) if queues else "all queues"
    click.echo(f"Launching a worker on {queue_names}")
    app.run_worker(queues=queues)


@cli.command()
@click.pass_obj
@handle_errors()
def scheduler(app: procrastinate.App):
    """
    Launch the scheduler process
    """
    click.echo(f"Launching scheduler")
    app.run_scheduler()


@cli.command()
@click.pass_obj
@handle_errors()
@click.argument("task")
@click.argument("json_args", required=False)
@click.option(
    "--lock", help="A lock string. Jobs sharing the same lock will not run concurrently"
)
@click.option("--at", help="ISO-8601 localized datetime after which to launch the job")
@click.option(
    "--in", "in_", type=int, help="Number of seconds after which to launch the job"
)
def defer(
    app: procrastinate.App,
    task: str,
    json_args: str,
    lock: Optional[str],
    at: Optional[str],
    in_: Optional[int],
):
    """
    Create a job from the given task, to be executed by a worker.
    TASK should be the name or dotted path to a task declared in the App object.
    JSON_ARGS should be a json object (a.k.a dictionnary) with the job parameters
    """
    # Loading json args
    args = load_json_args(json_args=json_args)

    if at is not None and in_ is not None:
        raise click.UsageError("Cannot use both --at and --in")

    schedule_at = get_schedule_at(at=at)
    schedule_in = get_schedule_in(in_=in_)

    # Retrieving the associated task
    task_obj = get_task(app=app, task_name=task)

    # Printing info
    str_kwargs = ", ".join(f"{k}={repr(v)}" for k, v in args.items())
    click.echo(f"Launching a job: {task}({str_kwargs})")

    # Finally launching the job
    task_obj.configure(
        lock=lock, schedule_at=schedule_at, schedule_in=schedule_in
    ).defer(**args)


def load_json_args(json_args) -> types.JSONDict:
    if json_args is None:
        return {}
    else:
        try:
            args = json.loads(json_args)
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


def get_task(app: procrastinate.App, task_name: str) -> tasks.Task:
    app.perform_import_paths()
    try:
        return app.tasks[task_name]
    except KeyError:
        raise click.BadArgumentUsage(f"Task {task_name} not found.")


@cli.command()
@click.pass_obj
@handle_errors()
@click.option(
    "--run/--text",
    default=True,  # a.k.a run
    help="Output the migration SQL as *text*, or *run* it on the DB directly (default)",
)
def migrate(app: procrastinate.App, run: bool):
    """
    Run database migrations and prepare the database.
    """
    migrator = app.migrator
    if run:
        click.echo("Launching migrations")
        migrator.migrate()
        click.echo("Done")
    else:
        click.echo(migrator.get_migration_queries(), nl=False)


def main():
    # https://click.palletsprojects.com/en/7.x/python3/
    os.environ.setdefault("LC_ALL", "C.UTF-8")
    os.environ.setdefault("LANG", "C.UTF-8")

    return cli()
