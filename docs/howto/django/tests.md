# Test Procrastinate interactions in a Django project

## Unit tests

There are different kind of tests you might want to do with Procrastinate in
a Django project. One such test is a unit test where you want fast tests that
don't hit the database.

For this, you can use the {py:class}`procrastinate.testing.InMemoryConnector`.

Here's an example pytest fixture you can write in your `conftest.py`:

```python
import pytest
from procrastinate import testing
from procrastinate.contrib.django import procrastinate_app

from mypackage.procrastinate import my_task

@pytest.fixture
def app():
    in_memory = testing.InMemoryConnector()

    # Replace the connector in the current app
    # Note that this fixture gives you the app back for convenience, but it's
    # the same instance as you'd get with `procrastinate.contrib.django.app`.
    with procrastinate_app.current_app.replace_connector(in_memory) as app_with_connector:
        yield app_with_connector

def test_my_task(app):
    # Run the task
    my_task.defer(a=1, b=2)

    # Access all the existing jobs
    jobs = app.connector.jobs
    assert len(jobs) == 1

    # Run the jobs
    app.run_worker(wait=False)
    assert task_side_effect() == "done"

    # Reset the in-memory pseudo-database. This usually isn't necessary if
    # you make small scoped tests as you'll use a new app fixture for each test
    # but it might come in handy.
    app.connector.reset()
```

:::{note}
`procrastinate.contrib.django.procrastinate_app.current_app` is not exactly
_documented_ but whatever instance this variable points to is what
will be returned as `procrastinate.contrib.django.app`. It's probably a bad
idea to manipulate this outside of tests.
:::

## Integration tests

Another kind of test, maybe more frequent within Django, would be an
integration test. In this kind of test you would use the database. You can use
Procrastinate normally with `procrastinate.contrib.django.app` in your tests.

You can use the procrastinate models to check if the jobs have been created
as expected.

```python
from procrastinate.contrib.django.models import ProcrastinateJob

from mypackage.procrastinate import my_task


def test_my_task():
    # Run the task
    my_task.defer(a=1, b=2)

    # Check the job has been created
    assert ProcrastinateJob.objects.filter(task_name="my_task").count() == 1
```

:::{note}
Registering a new task on the django procrastinate app within a test will
make this task available even after the test has run. You probably want to
avoid this, for example by creating a new app within each of those tests:

```python
from procrastinate.contrib.django import app

def test_my_task():
    new_app = procrastinate_app.ProcrastinateApp(app.connector)

    @new_app.task
    def my_task(a, b):
        return a + b

    my_task.defer(a=1, b=2)
    ...
```

:::

In addition, you can also run a worker in your integration tests. Whether you
use `pytest-django` or Django's `TestCase` subclasses, this requires some
additonal configuration.

1. In order to run the worker, use the syntax outlined here: {doc}`scripts`.
2. In order for Procrastinate to be able to use `SELECT FOR UPDATE`, use
   [`TransactionTestCase`]. With `TestCase`, you can't test code within a
   transaction with `select_for_update()`. If you use `pytest-django`, use
   the equivalent `@pytest.mark.django_db(transaction=True)`.
3. Lastly, there are useful arguments to pass to `run_worker`:
    - `wait=False` to exit the worker as soon as all jobs are done
    - `install_signal_handlers=False` to avoid messing with signals in your
      test runner
    - `listen_notify=False` to avoid running the listen/notify coroutine which
      is probably not needed in tests

[`TransactionTestCase`]: https://docs.djangoproject.com/en/5.0/topics/testing/tools/#transactiontestcase

```python
from procrastinate.contrib.django import app
from django.test import TransactionTestCase

from mypackage.procrastinate import my_task

class TestingTaskClass(TransactionTestCase):
    def test_task(self):
        # Run tasks
        my_task.defer(a=1, b=2)

        # Start worker
        app = app.with_connector(app.connector.get_worker_connector())
        app.run_worker(wait=False, install_signal_handlers=False, listen_notify=False)

        # Check task has been executed
        assert ProcrastinateJob.objects.filter(task_name="my_task").status == "succeeded"
```

```python
from procrastinate.contrib.django import app

from mypackage.procrastinate import my_task

@pytest.mark.django_db(transaction=True)
def test_task():
    # Run tasks
    my_task.defer(a=1, b=2)

    # Start worker
    app = app.with_connector(app.connector.get_worker_connector())
    app.run_worker(wait=False, install_signal_handlers=False, listen_notify=False)

    # Check task has been executed
    assert ProcrastinateJob.objects.filter(task_name="my_task").status == "succeeded"

# Or with a fixture
@pytest.fixture
def worker(transactional_db):
    def _():
        app = app.with_connector(app.connector.get_worker_connector())
        app.run_worker(wait=False, install_signal_handlers=False, listen_notify=False)
        return app
    return _

def test_task(worker):
    # Run tasks
    my_task.defer(a=1, b=2)

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
