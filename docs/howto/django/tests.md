# Test Procrastinate interactions in a Django project

## Unit tests

If you want to be able to run your code that uses Procrastinate in a unit test,
you can use the {py:class}`procrastinate.testing.InMemoryConnector`.

Here's an example pytest fixture you can write in your `conftest.py`:

```python
import pytest
from procrastinate import testing
from procrastinate.contrib.django import procrastinate_app

@pytest.fixture
def in_memory_app(monkeypatch):
    app = procrastinate_app.current_app.with_connector(
        testing.InMemoryConnector()
    )
    monkeypatch.setattr(procrastinate_app, "current_app", app)
    return app
```

:::{note}
`procrastinate.contrib.django.procrastinate_app.current_app` is not exactly
_documented_ but whatever instance this variable points to is what
will be returned as `procrastinate.contrib.django.app`. It's probably a bad
idea to use this outside of tests.
:::

## Integration tests

You can use Procrastinate normally with `procrastinate.contrib.django.app`
in your tests, though registering new tasks or loading tasks from blueprints
within your tests might lead to test isolation issues. If you need to
do that, you may want to use the trick described above to have a dedicated
app for each relevant test.

You can use the procrastinate models to check if the jobs have been created
as expected.

```python
from procrastinate.contrib.django.models import ProcrastinateJob

def test_my_task(app):
    # Run the task
    app.defer("my_task", args=(1, 2))

    # Check the job has been created
    assert ProcrastinateJob.objects.filter(task_name="my_task").count() == 1
```

In addition, you can also run a worker in your integration tests. Whether you
use `pytest-django` or Django's `TestCase` subclasses, his requires some
addiitonal configuration.

1. In order to run the worker, use the syntax outlined here: {doc}`scripts`.
2. In order for Procrastinate to be able to use `SELECT FOR UPDATE`, use
   [`TransactionTestCase`]. With `TestCase`, you can't test code within a
   transaction with `select_for_update()`. If you use `pytest-django`, use
   the equivalent `@pytest.mark.django_db(transaction=True)`.
3. Lastly, setup the worker using `wait=False` and
   `install_signal_handlers=False`. `wait=False` means that when all tasks are
   executed, the call will return. `install_signal_handlers=False` is optional
   and just here to keep the worker from changing the signal callbacks set by
   your test runner.

[`TransactionTestCase`]: https://docs.djangoproject.com/en/5.0/topics/testing/tools/#transactiontestcase

```python
from procrastinate.contrib.django import app
from django.test import TransactionTestCase

class TestingTaskClass(TransactionTestCase):
    def test_task(self):
        # Run tasks
        app.defer("my_task", args=(1, 2))

        # Start worker
        app = app.with_connector(app.connector.get_worker_connector())
        app.run_worker(wait=False, install_signal_handlers=False, listen_notify=True)

        # Check task has been executed
        assert ProcrastinateJob.objects.filter(task_name="my_task").status == "succeeded"
```

```python
from procrastinate.contrib.django import app

@pytest.mark.django_db(transaction=True)
def test_task():
    # Run tasks
    app.defer("my_task", args=(1, 2))

    # Start worker
    app = app.with_connector(app.connector.get_worker_connector())
    app.run_worker(wait=False, install_signal_handlers=False, listen_notify=True)

    # Check task has been executed
    assert ProcrastinateJob.objects.filter(task_name="my_task").status == "succeeded"

# Or with a fixture
@pytest.fixture
def worker(transactional_db):
    def _():
        app = app.with_connector(app.connector.get_worker_connector())
        app.run_worker(wait=False, install_signal_handlers=False, listen_notify=True)
        return app
    return _

def test_task(worker):
    # Run tasks
    app.defer("my_task", args=(1, 2))

    # Start worker
    worker()

    # Check task has been executed
    assert ProcrastinateJob.objects.filter(task_name="my_task").status == "succeeded"
```

## Making the models writable in tests

If you need to write to the procrastinate models in your tests, a setting is
provided: `PROCRASTINATE_READONLY_MODELS`. If set to `False`, the models will be
writable. You may want to use the `settings` fixture from `pytest-django` to
set this setting only for the tests that need it.

```python
@pytest.fixture
def procrastinate_writable_models(settings):
    settings.PROCRASTINATE_READONLY_MODELS = False
```

:::{warning}
This setting is only intended for tests.
:::
