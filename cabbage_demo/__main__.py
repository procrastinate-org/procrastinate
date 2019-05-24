import logging
import sys

import cabbage
from cabbage_demo.cabbage_app import task_manager


def main():
    logging.basicConfig(level="DEBUG")
    process = sys.argv[1]
    if process == "worker":
        queue = sys.argv[2]
        worker = cabbage.Worker(
            task_manager=task_manager, queue=queue, import_paths=["cabbage_demo.tasks"]
        )
        worker.run()

    else:
        from cabbage_demo import client

        return client.client()


if __name__ == "__main__":
    main()
