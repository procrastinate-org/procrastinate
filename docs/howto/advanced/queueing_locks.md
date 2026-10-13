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

`queueing_lock` allows a single job in `todo` status. Meanwhile, it allows multiple jobs to be in `doing` status.

To enforce that only one job runs at a time while limiting the queue size, you can combine `queueing_lock` with [lock](./locks.md).

A queueing lock limits admission to `todo`, rather than execution in `doing`.
When a worker starts a job, its status changes from `todo` to `doing`, freeing
that queueing-lock value for a new waiting job. Another worker may start the new
job while the first one is still running.

:::{figure} ../../images/queueing-and-execution-locks.png
:alt: With queueing_lock alone, at most one matching job waits in todo, but several may run in doing. Adding lock also limits doing to one matching job.
:width: 544px

Admission and execution limits for matching lock values.
[Editable SVG](../../images/queueing-and-execution-locks.svg).
[Edit diagram](https://svgdiagram.ai/diagram-sources/procrastinate-queueing-and-execution-locks?version=1).
:::

In the right-hand case, jobs share the same `queueing_lock` value **and** the
same `lock` value. At most one matching job waits and one runs; both states can
be occupied at the same time. The waiting job cannot be fetched until the
execution lock is available, even though a worker is free.

For example, give repeated maintenance jobs both limits:

```python
@app.task(queueing_lock="maintenance-pending", lock="maintenance-running")
def maintenance(): ...
```

The two strings need not be identical: each identifies a separate group of jobs.
A second waiting job with the same queueing-lock value still raises
{py:class}`AlreadyEnqueued`, as above. Locks apply across tasks and queues that
use matching values; see [execution locks](./locks.md) for ordering and scheduling
considerations.


You might also want to [schedule](./schedule.md) jobs for such task in the near future, which can be effective to throttle the task.
