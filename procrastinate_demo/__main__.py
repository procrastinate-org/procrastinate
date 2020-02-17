import logging

from procrastinate_demo import tasks
from procrastinate_demo.app import app


def main():
    logging.basicConfig(level="DEBUG")

    tasks.sum.defer(a=3, b=5)
    tasks.sum.defer(a=5, b=7)
    tasks.sum.defer(a=5, b="a")
    tasks.sum_plus_one.defer(a=4, b=7)
    tasks.sleep.configure(lock="a").defer(i=2)
    tasks.sleep.configure(lock="a").defer(i=3)
    tasks.sleep.configure(lock="a").defer(i=4)
    tasks.random_fail.defer()

    app.close_connection()


if __name__ == "__main__":
    main()
