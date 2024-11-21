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


async def operations(cli, logs_path: pathlib.Path, subtests):
    with subtests.test(msg="subtest_simple_defer_and_execute"):
        await subtest_simple_defer_and_execute(cli, logs_path)

    # Periodic: add a periodic task, launch a worker, check that the task is
    # executed
    # with subtests.test(msg="periodic"):
    #     # TODO : put it in its own function
    #     # Actually assert something
    #     cli("worker", env={"TEST_ADD_PERIODIC": "1"})

    # Defer 2 tasks without workers with the same queueing lock, and check the
    # 2nd one can't be deferred

    # Defer 1 "long" task & 1 "short" task with the same lock, and check that
    # the long task is executed first even with concurrency=2

    # Defer 20 jobs and launch a worker with concurrency=20 and check that all
    # jobs are executed in parallel

    # Call the shell and check that it works on listing jobs

    # Also implement as acceptance test:
    # test the 3 apis for deferring a job
    # cancel_job_by_id_async (with /out delete)(async job cancels gracefully)
    # concurrency
    # fetch_job_polling_interval
    # shutdown_timeout
    # Traceback in logs
    # periodic

    # Maybe better as integration tests:
    # queuing lock
    # locks
    # shell list
    # Priority


async def subtest_simple_defer_and_execute(cli, logs_path: pathlib.Path):
    # Defer a task, launch a worker, interrupt the worker, check that the task
    # was run

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
