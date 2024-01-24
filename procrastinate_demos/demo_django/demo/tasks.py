from __future__ import annotations

import time

from procrastinate.contrib.django import app

from .models import Book


@app.task(queue="index")
def index_book(book_id: int):
    time.sleep(5)
    # Sync ORM call
    assert Book.objects.filter(id=book_id).exists()
    set_indexed.defer(book_id=book_id)


@app.task(queue="index")
async def set_indexed(book_id: int):
    # Async ORM call
    await Book.objects.filter(id=book_id).aupdate(indexed=True)
