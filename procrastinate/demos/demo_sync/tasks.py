from __future__ import annotations

from .app import app


@app.task(queue="sums")
def sum(a: int, b: int) -> None:
    print(f"{a} + {b} = {a + b}")


@app.task(queue="defer")
def defer():
    sum.defer(a=1, b=2)
