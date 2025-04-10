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
{py:class}`AlreadyEnqueued` exception, which you can choose to ignore.

In the command line interface (see {doc}`../basics/defer`), you can use `--queueing-lock` and
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

Queueing lock can also be interpolated with the parameters sent to the task.
In this example:

```
@app.task(queueing_lock="my_lock_value_{param_1}")
def my_task(param_1="aaa", **kwargs):
    ...

```

the queing lock value will be `my_lock_value_aaa`. (Under the hood we are invocating the
method .format(\*\*task_kwargs) of the queueing_lock's value.)

`queueing_lock` allows a single job in `todo` status. Meanwhile, it allows multiple jobs to be in `doing` status.

To enforce that only one job runs at a time while limiting the queue size, you can combine `queueing_lock` with [lock](./locks.md).

You might also want to [schedule](./schedule.md) jobs for such task in the near future, which can be effective to throttle the task.
