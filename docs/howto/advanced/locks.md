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
:::

If you plan to use the same lock for every job deferred from the same task, you can
define the value when you register the task:

```
@app.task(lock="my_lock_value")
def my_task(**kwargs):
    ...
```

## Locks and Priority

When multiple jobs share the same lock, they are processed one at a time in a specific order:
- descending priority (higher priority first)
- ascending creation time (older job first)

If any job with the same lock is running, all other jobs with that lock must wait. A high-priority job cannot jump ahead of a currently running job, regardless of the running job's priority.
