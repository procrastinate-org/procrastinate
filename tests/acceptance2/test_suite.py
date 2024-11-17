# There are 3 parameters we want to control in the acceptance tests:
# - The connector class
# - The migrations of the DB (pre-migrations or post-migrations)
# - The version of the code to test (current or stable)
#
# We don't want to run all the combinations of these parameters. Also, we'll
# want to make it easy to add new dimensions, new values for the dimensions or
# new tested combinations of dimensions.
# For every combination, the tests should be roughly the same: defer some
# tasks that involve a few important features of Procrastinate, run a couple
# of workers, after a few seconds, send a signal to the workers to stop, and
# check that the tasks have been executed
from __future__ import annotations

import asyncio
import pathlib

import pytest

from . import utils


async def operations(cli, logs_path: pathlib.Path):
    await cli("defer", "app.t1", '{"a": 1}')
    # launch worker
    try:
        await asyncio.wait_for(cli("worker"), timeout=1)
    except utils.InterruptedSubprocess as exc:
        assert exc.exit_code == 0
        logs_worker = exc.stderr
    else:
        assert False, "Worker should have been interrupted"

    assert "t1" in logs_worker

    with logs_path.open("r") as f:
        assert f.read() == "t1 1\n"


@pytest.mark.parametrize(
    "include_post_migrations, lib_version, env, extras",
    [
        (True, "current", {}, None),
        (False, "current", {}, None),
        (False, "stable", {}, None),
        (
            True,
            "current",
            {"TEST_CONNECTOR": "procrastinate.contrib.aiopg.AiopgConnector"},
            ["aiopg"],
        ),
    ],
)
async def test_scenario(
    prepare_acceptance_test, include_post_migrations, lib_version, env, extras
):
    run = await prepare_acceptance_test(
        include_post_migrations=include_post_migrations,
        lib_version=lib_version,
        additional_env=env,
        operations=operations,
        extras=extras,
    )

    await run()
