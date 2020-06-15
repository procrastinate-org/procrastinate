import os
import subprocess

import pytest

APP_MODULE = "tests.acceptance.app"


@pytest.fixture
def process_env(connection_params):
    env = os.environ.copy()
    env.update(
        {
            "PROCRASTINATE_APP": f"{APP_MODULE}.app",
            "PROCRASTINATE_VERBOSE": "3",
            "PROCRASTINATE_DEFER_UNKNOWN": "True",
            "PGDATABASE": connection_params["dbname"],
        }
    )
    return env


@pytest.fixture
def defer(process_env):
    from .app import json_dumps

    def func(task_name, args=None, app=None, **kwargs):
        args = args or []
        app_args = ["--app", f"{APP_MODULE}.{app}"] if app else []
        full_task_name = f"{APP_MODULE}.{task_name}"
        subprocess.check_output(
            [
                "procrastinate",
                *app_args,
                "defer",
                full_task_name,
                *args,
                json_dumps(kwargs),
            ],
            env=process_env,
        )

    return func
