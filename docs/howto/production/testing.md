# Test your code that uses Procrastinate

Procrastinate defines an {py:class}`InMemoryConnector` that will speed up your tests,
remove dependency to PostgreSQL and allow you to have tasks run in a
controlled way.

To use it, you can do:

```python
from procrastinate import testing
from mypackage.procrastinate import my_app, my_task

@pytest.fixture
def app():
    in_memory = testing.InMemoryConnector()

    # Replace the connector in the current app
    # Note that this fixture gives you the app back for covenience,
    # but it's the same instance as `my_app`.
    with my_app.replace_connector(in_memory) as app:
        yield app


def test_my_task(app):
    my_task.defer(...)

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
