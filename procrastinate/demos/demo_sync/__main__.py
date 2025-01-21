from __future__ import annotations

import json
import logging

from . import app as app_module
from . import tasks


def main():
    logging.info("Running app in sync context")

    with app_module.app.open():
        print("Enter the following to defer a task:")
        print(""" - 'sum {"a": 1, "b": 2}' for a task that sums two numbers""")
        print(" - 'defer' for a task that defers another task")
        print("Enter an empty line to quit")
        print()
        while True:
            response = (input("Your input: ")).strip()
            if not response:
                break
            command, *args = (response).split(maxsplit=1)
            task = {"sum": tasks.sum, "defer": tasks.defer}.get(command)
            kwargs = json.loads("".join(args) or "{}")
            if not task:
                print("Invalid command")
                continue

            task.defer(**kwargs)


if __name__ == "__main__":
    logging.basicConfig(level="DEBUG")
    main()
