# {term}`Defer` a job

There are several ways to do this.

In the following examples, the task will be:

```
@app.task(queue="some_queue")
def my_task(a: int, b:int):
    pass
```

Task name is `my_module.my_task`.

## The direct way

```
my_task.defer(a=1, b=2)
```

## With parameters

```
my_task.configure(
    lock="the name of my lock",
    schedule_in={"hours": 1},
    queue="not_the_default_queue"
).defer(a=1, b=2)
```

See details in {py:meth}`Task.configure`

## Create a job pattern, launch multiple jobs

```
pattern = my_task.configure(task_kwargs={"a": 1})

pattern.defer(b=2)
pattern.defer(b=3)
pattern.defer(b=4)
```

## Defer a job if you can't access the task

This is useful if the code that defers jobs is not in the same code base as the code
that runs the jobs. You can defer a job with just the name of its task.

```
app.configure_task(name="my_module.my_task", queue="some_queue").defer(a=1, b=2)
```

Any parameter you would use for {py:meth}`Task.configure` can be used in
{py:meth}`App.configure_task`.

## From the command line

```console
$ procrastinate defer my_module.my_task '{"a": 1, "b": 2}'
```

If the task is not registered, but you want to defer it anyway:

```console
$ procrastinate defer --unknown my_module.my_task '{"a": 1, "b": 2}'
$ # or
$ export PROCRASTINATE_DEFER_UNKNOWN=1
$ procrastinate defer my_module.my_task '{"a": 1, "b": 2}'
```
