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
    with procrastinate_app.current_app.replace_connector(in_memory) as app:
        yield app

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

In addition, you can also run a worker in your integration tests.

### DjangoTestingConnector and Pytest Plugin

If you need to test jobs while being closer to reality—like modifying job scheduling via the ORM—you can use the `DjangoTestingConnector`. This connector leverages your test database but handles `listen/notify` in-memory.

To make things easier, Procrastinate provides a pytest plugin (automatically enabled if both `pytest` and `django` are installed). It offers the `run_procrastinate_jobs` and `arun_procrastinate_jobs` fixtures, which act as a shortcut to replace the connector and run the worker.

Here is an example:

```python
import pytest
from procrastinate.contrib.django.models import ProcrastinateJob
from mypackage.procrastinate import my_task

@pytest.mark.django_db(transaction=True)
def test_task(run_procrastinate_jobs):
    # Run tasks
    my_task.defer(a=1, b=2)

    # You can interact with jobs using the ORM to mimic reality
    # (e.g. changing scheduled_at or statuses)

    # Process awaiting jobs
    run_procrastinate_jobs()

    # Check task has been executed
    assert ProcrastinateJob.objects.filter(task_name="my_task").first().status == "succeeded"

@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_async_task(arun_procrastinate_jobs):
    await my_task.defer_async(a=1, b=2)
    await arun_procrastinate_jobs()
```

### Time traveling with freezegun

You can also use tools like `freezegun` with `run_procrastinate_jobs` to test scheduled jobs by traveling through time. Note that if you intend to travel through time or modify jobs via ORM, you must have `transaction=True` on your `django_db` marker.

```python
import datetime
import pytest
import freezegun
from procrastinate.contrib.django.models import ProcrastinateJob
from mypackage.procrastinate import my_task

@pytest.mark.django_db(transaction=True)
def test_task_time_travel(run_procrastinate_jobs):
    with freezegun.freeze_time("2025-01-01T00:00:00Z"):
        my_task.defer(a=1, b=2)

        # Modify the job via ORM to schedule it for tomorrow
        ProcrastinateJob.objects.update(
            scheduled_at=datetime.datetime(2025, 1, 2, 0, 0, 0, tzinfo=datetime.timezone.utc)
        )

        # Worker shouldn't pick it up yet
        run_procrastinate_jobs()
        assert ProcrastinateJob.objects.filter(status="todo").exists()

    with freezegun.freeze_time("2025-01-02T01:00:00Z"):
        # The job is now ready to be processed
        run_procrastinate_jobs()
        assert ProcrastinateJob.objects.filter(status="succeeded").exists()
```

### Manual configuration without the pytest plugin

If you use `pytest-django` without using the fixtures, or Django's `TestCase` subclasses, running a worker requires some additional configuration.

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
from procrastinate.contrib.django.testing import DjangoTestingConnector
from django.test import TransactionTestCase

from mypackage.procrastinate import my_task

class TestingTaskClass(TransactionTestCase):
    def test_task(self):
        # Run tasks
        my_task.defer(a=1, b=2)

        # Start worker
        with app.replace_connector(DjangoTestingConnector()):
            app.run_worker(wait=False, install_signal_handlers=False, listen_notify=False)

        # Check task has been executed
        assert ProcrastinateJob.objects.filter(task_name="my_task").first().status == "succeeded"
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
