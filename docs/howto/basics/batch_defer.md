# Batch defer multiple jobs

Instead of deferring each job one by one, you can defer multiple jobs at once using the `batch_defer` resp. `batch_defer_async` method. This is useful when you want to defer a large number of jobs in a single call, which can be more efficient than deferring them one by one.

Let's assume the following task:

```python
@app.task(queue="some_queue")
def my_task(a: int, b:int):
    pass
```

## The direct way

By using the sync method:

```python
my_task.batch_defer(
    *[
        {"a": 1, "b": 2},
        {"a": 3, "b": 4},
        {"a": 5, "b": 6},
    ]
)
```

Or the async method:

```python
await my_task.batch_defer_async(
    *[
        {"a": 1, "b": 2},
        {"a": 3, "b": 4},
        {"a": 5, "b": 6},
    ]
)
```

## With parameters

Using the sync defer method:

```python
my_task.configure(
    lock="the name of my lock",
    schedule_in={"hours": 1},
    queue="not_the_default_queue"
).batch_defer(
    *[
        {"a": 1, "b": 2},
        {"a": 3, "b": 4},
        {"a": 5, "b": 6},
    ]
)

# or
await my_task.configure(
    lock="the name of my lock",
    schedule_in={"hours": 1},
    queue="not_the_default_queue"
).batch_defer_async(
    *[
        {"a": 1, "b": 2},
        {"a": 3, "b": 4},
        {"a": 5, "b": 6},
    ]
)
```

:::{warning}
Don't batch defer multiple jobs where the task has the same configured queuing lock, because that
would directly raise an `AlreadyEnqueued` exception and none of those jobs are deferred (the
database transaction will be fully rolled back).
See {doc}`queueing locks <../advanced/queueing_locks>` for more information.
