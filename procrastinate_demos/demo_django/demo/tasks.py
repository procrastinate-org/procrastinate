from __future__ import annotations

import time

from django.db import transaction

from procrastinate import App, Blueprint
from procrastinate.contrib.django import app

from .models import Book


@app.task(queue="index")
@transaction.atomic
def index_book(book_id: int):
    time.sleep(5)
    # Sync ORM call
    assert Book.objects.filter(id=book_id).exists()
    set_indexed.defer(book_id=book_id)


# Showcasing a task using blueprints. This is not mandatory at all.
# The blueprint is loaded in PROCRASTINATE_ON_APP_READY
blueprint = Blueprint()


@blueprint.task(queue="index")
async def set_indexed(book_id: int):
    # Async ORM call
    await Book.objects.filter(id=book_id).aupdate(indexed=True)


def on_app_ready(app: App):
    app.add_tasks_from(blueprint, namespace="bp")
