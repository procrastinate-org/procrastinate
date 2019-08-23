import contextlib
import logging
import os
from typing import Iterable, Optional

import click

import procrastinate
from procrastinate import exceptions

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
    return {0: logging.WARNING, 1: logging.INFO, 2: logging.DEBUG}.get(
        min((2, verbosity)), 0
    )


def set_verbosity(ctx: click.Context, param: click.Parameter, value: int) -> int:
    level = get_log_level(verbosity=value)
    logging.basicConfig(level=level)
    logger.info(f"Log level set to {logging.getLevelName(level)}")
    return value


@contextlib.contextmanager
def handle_errors():
    try:
        yield
    except exceptions.procrastinateException as exc:
        raise click.ClickException(str(exc))


def print_version(ctx, __, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo(f"{PROGRAM_NAME} {procrastinate.__version__}")
    click.echo(f"License: {procrastinate.__license__}")
    ctx.exit()


@click.group(context_settings=CONTEXT_SETTINGS)
@click.pass_context
@click.option("--app", help="Dotted path to the Procrastinate app")
@click.option(
    "-v",
    "--verbose",
    is_eager=True,
    callback=set_verbosity,
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
def worker(app: Optional[procrastinate.App], queue: Iterable[str]):
    """
    Launch a worker, listening on the given queues (or all queues)
    """
    queues = list(queue) or None
    queue_names = ", ".join(queues) if queues else "all queues"
    click.echo(f"Launching a worker on {queue_names}")
    app.run_worker(queues=queues)


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
    Launch a worker, listening on the given queues (or all queues)
    """
    migrator = app.migrator
    if run:
        click.echo("Launching migrations")
        migrator.migrate()
        click.echo("Done")
    else:
        click.echo(migrator.get_migration_queries())


def main():
    # https://click.palletsprojects.com/en/7.x/python3/
    os.environ.setdefault("LC_ALL", "C.UTF-8")
    os.environ.setdefault("LANG", "C.UTF-8")

    return cli()
