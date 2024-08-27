# Define a task

Specify a sync task with:

```python
@app.task(...)
def mytask(argument, other_argument):
    ...
```

:::{note}
Each sync task runs in its own thread (independently of the worker thread).
:::

Or an async task with:

```python
@app.task(...)
async def mytask(argument, other_argument):
    ...
```

:::{note}
All async tasks run in the same event loop.
:::

See {py:meth}`App.task` for the exact parameters. In particular, you can define values for
`queue`, `lock` and  `queueing_lock` that will be used as default values when
calling {py:meth}`Task.configure` or {py:meth}`Task.defer` on this task.

If you're OK with all the default parameters, you can omit parentheses after
`task`:

```python
@app.task
def mytask(argument, other_argument):
    ...

# or
@app.task
async def mytask(argument, other_argument):
    ...
```
