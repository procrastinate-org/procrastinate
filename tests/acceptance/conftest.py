import os
import subprocess

import pytest

import procrastinate

APP_MODULE = "tests.acceptance.app"


@pytest.fixture
def process_env(connection_params):
    def _(*, app="app"):
        env = os.environ.copy()
        env.update(
            {
                "PROCRASTINATE_APP": f"{APP_MODULE}.{app}",
                "PROCRASTINATE_VERBOSE": "3",
                "PROCRASTINATE_DEFER_UNKNOWN": "True",
                "PGDATABASE": connection_params["dbname"],
            }
        )
        return env

    return _


@pytest.fixture
def defer(process_env):
    from .app import json_dumps

    def func(task_name, args=None, app="app", **kwargs):
        args = args or []
        full_task_name = f"{APP_MODULE}.{task_name}"
        subprocess.check_output(
            ["procrastinate", "defer", full_task_name, *args, json_dumps(kwargs)],
            env=process_env(app=app),
        )

    return func


@pytest.fixture
async def async_app_explicit_open(not_opened_aiopg_connector):
    app = await procrastinate.App(connector=not_opened_aiopg_connector).open_async()
    yield app
    await app.close_async()
