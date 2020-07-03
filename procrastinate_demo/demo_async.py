"""
- cursor_factory
- launch migrations


---
- cli app can be callable/awaitable
"""
import asyncio

import aiopg
import psycopg2.extras

import procrastinate

conf = {}

app = procrastinate.App(connector=procrastinate.AiopgConnector(password="password"))


async def main():
    async with aiopg.create_pool("", cursor_factory=psycopg2.extras.RealDictCursor, password=app.kwargs["password"]) as pool:
        await app.open_async(pool)
        await task.defer_async()


@app.task()
def task():
    print("Hello world!")



async def open_app():
    pool = await get_pool()
    await app.open_async(pool=pool)


if __name__ == '__main__':
    asyncio.run(main())
