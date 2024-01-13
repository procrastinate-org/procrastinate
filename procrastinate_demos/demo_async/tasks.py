from __future__ import annotations

from .app import app


@app.task(queue="sums")
async def sum(a, b):
    return a + b


@app.task(queue="defer")
async def defer():
    await sum.defer_async(a=1, b=2)
