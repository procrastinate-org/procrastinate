# Ensure jobs run sequentially and in order

In this section, we'll see **how** to setup locks. If you want to know
more about the locking feature (mainly the **why**), head to the Discussions
section (see {ref}`discussion-locks`).

When deferring a job, we can provide a lock string to the `configure` method:

```
my_task.configure(lock=customer.id).defer(a=1)
my_other_task.configure(lock=customer.id).defer(b=2)
```

Or if we're deferring the same task with the same lock multiple times, we can call
configure just once:

```
job_description = my_task.configure(lock=customer.id)
job_description.defer(a=1)
job_description.defer(a=2)
```

In both cases, the second task cannot run before the first one
has ended (successfully or not).

:::{warning}
If a task with a `scheduled_at` argument is deferred with a lock, then
following tasks can only run after this one is processed, which
may be in a long time.

Similarly, if the oldest task of a lock is in a queue that no worker consumes, the
other tasks are blocked.

This is a consequence of the ordering guarantee. If you only need mutual exclusion
and don't care about ordering, use `lock_mode="mutex"` (see below).
:::

If you plan to use the same lock for every job deferred from the same task, you can
define the value when you register the task:

```
@app.task(lock="my_lock_value")
def my_task(**kwargs):
    ...
```

## Lock modes

A lock always guarantees that no two jobs sharing it run simultaneously. What differs
between the two modes is whether a job that is merely *waiting* also holds the lock.

`lock_mode="ordered"` (the default) additionally guarantees that jobs sharing the lock
**start in order**. To do that, the job at the head of the lock keeps the lock reserved
even when it isn't runnable yet, which is what the warning above describes.

`lock_mode="mutex"` only holds the lock while a job actually runs. Jobs sharing the lock
may then start in any order, but a job that isn't runnable yet never blocks the others:

```
my_task.configure(lock=customer.id, lock_mode="mutex").defer(a=1)
```

Use `"mutex"` when the lock protects a shared resource (an external API account, a row,
a file) and the order in which jobs run is irrelevant. A typical case is a job that
retries with a long backoff: under `"ordered"` it would hold up every other job on the
same lock for the whole backoff, while under `"mutex"` the others keep running.

:::{note}
The mode should be the same for every job sharing a given lock string. Procrastinate
does not enforce this, and mixing modes on one lock gives confusing results.
:::

## Locks and Priority

When multiple jobs share the same `"ordered"` lock, they are processed one at a time in
a specific order:
- descending priority (higher priority first)
- ascending creation time (older job first)

If any job with the same lock is running, all other jobs with that lock must wait. A high-priority job cannot jump ahead of a currently running job, regardless of the running job's priority.

With a `"mutex"` lock, this ordering is not guaranteed: jobs still run one at a time, but
any of the runnable ones may be picked.
