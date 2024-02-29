"""
URL configuration for demo_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from __future__ import annotations

from django.contrib import admin
from django.contrib.staticfiles import views
from django.urls import path, re_path

from procrastinate_demos.demo_django.demo.views import CreateBookView, ListBooksView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", ListBooksView.as_view(), name="list_books"),
    path("create/", CreateBookView.as_view(), name="create_book"),
    re_path(r"^static/(?P<path>.*)$", views.serve),
]
