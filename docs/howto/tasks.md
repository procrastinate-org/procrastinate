# Define a task

You can specify a task with:

```
@app.task(...)
def mytask(argument, other_argument):
    ...
```

See {any}`App.task` for the exact parameters. In particular, you can define values for
`queue`, `lock` and  `queueing_lock` that will be used as default values when
calling {any}`Task.configure` or {any}`Task.defer` on this task.

If you're OK with all the default parameters, you can omit parentheses after
`task`:

```
@app.task
def mytask(argument, other_argument):
    ...
```
