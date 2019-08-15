import logging

from procrastinate_demo import tasks

logger = logging.getLogger(__name__)


def client():
    tasks.sum.defer(a=3, b=5)
    tasks.sum.defer(a=5, b=7)
    tasks.sum.defer(a=5, b="a")
    tasks.sum_plus_one.defer(a=4, b=7)
    tasks.sleep.configure(lock="a").defer(i=2)
    tasks.sleep.configure(lock="a").defer(i=3)
    tasks.sleep.configure(lock="a").defer(i=4)
    tasks.random_fail.defer()
