# Ensure tasks don't accumulate in the queue

Some kind of tasks implement actions that absolutely need to be done. Others, for
example cleanup tasks, implement actions that would ideally need to be done often, but
could easily be missed once in a while. In particular, in case of a slowdown in job
processing, your queue can sometimes become filled with jobs that don't really add
much value.

You can tell Procrastinate that a specific set of jobs can never appear more than once
in the queue, by using a queueing lock:

```
my_task.configure(queueing_lock="arbitrary_string").defer(a=1)
my_task.configure(queueing_lock="arbitrary_string").defer(a=2)
```

Trying to defer a task when the `queueing_lock` is active will result in an
{any}`AlreadyEnqueued` exception, which you can choose to ignore.

In the command line interface (see {any}`./defer`), you can use `--queueing-lock` and
`--ignore-already-enqueued/-i` to control how queueing locks are used:

```console
$ procrastinate defer --queueing-lock=maintenance --ignore-already-enqueued \
    my.maintenance.task
```

If you plan to use the same queueing lock for every job deferred from the same task, you
can define the value when you register the task:

```
@app.task(queueing_lock="my_lock_value")
def my_task(**kwargs):
    ...
```
