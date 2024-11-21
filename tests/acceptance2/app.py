# This file is meant to be used in isolation from the test suite.
# It should test that the currently installed version of Procrastinate works as
# expected, with the current database migrations.
# Details on how to run the test can be passed as environment variables.
from __future__ import annotations

import asyncio
import dataclasses
import importlib
import json
import os
import pathlib

import procrastinate


@dataclasses.dataclass
class Settings:
    CONNECTOR: str = "procrastinate.PsycopgConnector"
    CONNECTOR_ARGS: str = "{}"
    DESTINATION: str = str(pathlib.Path(__file__).parent)
    ADD_PERIODIC: str = "false"

    @classmethod
    def from_env(cls, prefix: str = "TEST_") -> Settings:
        return cls(
            **{
                key: os.environ[prefix + key]
                for key in cls.__dataclass_fields__
                if prefix + key in os.environ
            }
        )


settings = Settings.from_env()


def class_for_name(dotted_path: str) -> type:
    module_name, class_name = dotted_path.rsplit(".", 1)

    # load the module, will raise ImportError if module cannot be loaded
    m = importlib.import_module(module_name)
    # get the class, will raise AttributeError if class cannot be found
    c = getattr(m, class_name)
    return c


def log(*args):
    print(*args)
    with pathlib.Path(settings.DESTINATION).open("a") as f:
        f.write(" ".join(str(e) for e in args) + "\n")


connector_class = class_for_name(settings.CONNECTOR)
connector_args = json.loads(settings.CONNECTOR_ARGS)

app = procrastinate.App(connector=connector_class(**connector_args))


@app.task
def t1(a: int):
    log("t1", a)


@app.task
async def t2(a: int):
    log("t2", a)
    await asyncio.sleep(0)


@app.task
def t3(a: int):
    log("t3", a)
    t1.defer(a=a)


@app.task
async def t4(a: int):
    log("t4", a)
    await t2.defer_async(a=a)


@app.task
async def sleep(a: float):
    log("t5", a)
    await asyncio.sleep(a)


if settings.ADD_PERIODIC.lower()[0] in ["y", "t", "1"]:

    @app.periodic(cron="* * * * * *")
    @app.task
    async def periodic(timestamp: int, a: float):
        log("periodic", timestamp)
        await asyncio.sleep(a)
