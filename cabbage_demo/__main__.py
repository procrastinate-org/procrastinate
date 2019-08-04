import logging
import sys

from cabbage_demo.cabbage_app import app


def main():
    logging.basicConfig(level="DEBUG")
    process = sys.argv[1]
    if process == "worker":
        try:
            queues = [e.strip() for e in sys.argv[2].split(",")]
        except IndexError:
            queues = None

        app.run_worker(queues=queues)

    else:
        from cabbage_demo import client

        return client.client()


if __name__ == "__main__":
    main()
