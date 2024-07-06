# Test your code that uses Procrastinate

Procrastinate defines an {py:class}`InMemoryConnector` that will speed up your tests,
remove dependency to PostgreSQL and allow you to have tasks run in a
controlled way.

To use it, you can do:

```python
from mypackage.procrastinate import my_app, my_task

@pytest.fixture
def app():
    in_memory = procrastinate.testing.InMemoryConnector()

    with my_app.replace_connector(in_memory) as app_with_connector:
        yield app_with_connector


def test_my_code(app):
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
