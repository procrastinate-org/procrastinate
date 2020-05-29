import os
import subprocess

import pytest


@pytest.fixture
def process_env(connection_params):
    env = os.environ.copy()
    env.update(
        {
            "PROCRASTINATE_APP": "tests.acceptance.app.app",
            "PROCRASTINATE_VERBOSE": "3",
            "PGDATABASE": connection_params["dbname"],
        }
    )
    return env


@pytest.fixture
def defer(process_env):
    from .app import json_dumps

    def func(task_name, lock=None, queue=None, **kwargs):
        lock_args = ["--lock", lock] if lock else []
        queue_args = ["--queue", queue] if queue else []
        full_task_name = f"tests.acceptance.app.{task_name}"
        subprocess.check_output(
            [
                "procrastinate",
                "defer",
                full_task_name,
                *lock_args,
                *queue_args,
                json_dumps(kwargs),
            ],
            env=process_env,
        )

    return func
