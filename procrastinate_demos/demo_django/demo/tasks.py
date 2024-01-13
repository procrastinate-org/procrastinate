from __future__ import annotations

import time

from ..procrastinate_app import app
from .models import Book


@app.task(queue="index")
def index_book(book_id: int):
    time.sleep(5)
    set_indexed.defer(book_id=book_id)


@app.task(queue="index")
def set_indexed(book_id: int):
    Book.objects.filter(id=book_id).update(indexed=True)
