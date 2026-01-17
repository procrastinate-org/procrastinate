from __future__ import annotations

from typing import Any

from django.views import generic

from . import models, tasks


class CreateBookView(generic.CreateView):
    model = models.Book
    fields = ["title", "author"]
    success_url = "/"

    def form_valid(self, form: Any):
        response = super().form_valid(form)
        tasks.index_book.defer(book_id=self.object.id)  # pyright: ignore[reportOptionalMemberAccess]
        return response


class ListBooksView(generic.ListView):
    model = models.Book
