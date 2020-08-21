import asyncio
import logging

from procrastinate_demo import app, tasks


def main():
    logging.info("Running app in sync context")

    app.app.open()

    tasks.sum.defer(a=3, b=5)
    tasks.sum.defer(a=5, b=7)
    tasks.sum.defer(a=5, b="a")
    tasks.sum_plus_one.defer(a=4, b=7)
    tasks.sleep.configure(lock="a").defer(i=2)
    tasks.sleep.configure(lock="a").defer(i=3)
    tasks.sleep.configure(lock="a").defer(i=4)
    tasks.random_fail.defer()

    app.app.close()


async def main_async():
    logging.info("Running app in async context")

    await app.app.open_async()

    await tasks.sum.defer_async(a=3, b=5)
    await tasks.sum.defer_async(a=5, b=7)
    await tasks.sum.defer_async(a=5, b="a")
    await tasks.sum_plus_one.defer_async(a=4, b=7)
    await tasks.sleep.configure(lock="a").defer_async(i=2)
    await tasks.sleep.configure(lock="a").defer_async(i=3)
    await tasks.sleep.configure(lock="a").defer_async(i=4)
    await tasks.random_fail.defer_async()

    await app.app.close_async()


if __name__ == "__main__":
    logging.basicConfig(level="DEBUG")
    if app.is_async:
        asyncio.get_event_loop().run_until_complete(main_async())
        # asyncio.run(main_async())  # python3.7 only
    else:
        main()
