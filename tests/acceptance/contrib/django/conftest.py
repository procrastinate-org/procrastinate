import os

import pytest

from procrastinate.contrib.django.sync_app import App

APP_MODULE = "tests.acceptance.contrib.django.app"


@pytest.fixture
def process_env(connection_params):
    def _(*, app="app"):
        env = os.environ.copy()
        env.update(
            {
                "PROCRASTINATE_APP": f"{APP_MODULE}.{app}",
                "PROCRASTINATE_VERBOSE": "3",
                "PROCRASTINATE_DEFER_UNKNOWN": "True",
                "PGDATABASE": connection_params["dbname"],
                "PYTHONUNBUFFERED": "1",
            }
        )
        return env

    return _


@pytest.fixture
def django_app_explicit_open(not_opened_django_connector):
    app = App(connector=not_opened_django_connector).open()
    yield app
    app.close()


@pytest.fixture
def django_app_context_manager(not_opened_django_connector):
    with App(connector=not_opened_django_connector).open() as app:
        yield app


@pytest.fixture(
    params=[
        pytest.param(False, id="explicit open"),
        pytest.param(True, id="context manager open"),
    ]
)
def django_app(request, django_app_explicit_open, django_app_context_manager):
    if request.param:
        yield django_app_explicit_open
    else:
        yield django_app_context_manager
