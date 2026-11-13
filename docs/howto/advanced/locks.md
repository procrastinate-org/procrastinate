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

This is a consequence of the ordering guarantee. If you only need mutual exclusion
and don't need a job scheduled for later to reserve the lock, use `lock_mode="mutex"`
(see below).

Similarly, if the oldest task of a lock is in a queue that no worker consumes, the
other tasks are blocked. Note that `lock_mode="mutex"` does **not** help here; see
{ref}`what-holds-a-lock` for why.
:::

If you plan to use the same lock for every job deferred from the same task, you can
define the value when you register the task:

```
@app.task(lock="my_lock_value")
def my_task(**kwargs):
    ...
```

## Lock modes

Both lock modes guarantee that **no two jobs sharing a lock ever run at the same time**.
What differs is whether a job *scheduled for the future* still holds the lock for the
ones behind it.

`lock_mode="ordered"` (the default) holds the lock regardless. That is what guarantees
jobs sharing a lock are started in order, and it is also why the caveat above exists: a
job scheduled for tomorrow keeps the whole lock idle until then.

`lock_mode="mutex"` behaves exactly like `"ordered"`, **except that a job scheduled for
the future steps aside** instead of holding the lock until it is due:

```python
my_task.configure(lock=customer.id, lock_mode="mutex").defer(a=1)
```

Among the jobs that *are* due, a `"mutex"` lock still hands them out one at a time in
the same priority-then-creation order described below. It does not make execution
unordered; it only stops a job that isn't due yet from blocking the ones that are.

Use `"mutex"` when the lock protects a shared resource (an external API account, a row,
a file) and you don't need a job scheduled for later to reserve it. The typical case is
a job retried with a long backoff: under `"ordered"` it holds up every other job on the
same lock for the whole backoff, while under `"mutex"` the others keep running.

(what-holds-a-lock)=

### What holds a lock

Consider jobs `A` with id 1 and `B` with id 2, they both share the same lock value and
priority.

If job `A` is due, then it blocks job `B` from running. This is true whether there
is a worker consuming `A`'s queue or not.

If job `A` is scheduled later:
- If job `A` has `lock_mode="mutex"`, then it **doesn't** block job `B`.
- If job `A` has `lock_mode="ordered"` (the default), then it blocks `B`.

If job `A` is running, then it blocks `B` from running, whatever their priorities.

If `A` had a lower priority than `B`, the roles would be swapped: `B` would come first,
and everything above applies with `A` and `B` exchanged.

It might be surprising that with `lock_mode="mutex"`, you can still end up with jobs
sharing a lock stuck for a long time waiting for a job on a queue that no worker
consumes.

The reason is that workers must agree on what holds a lock. If they disagreed, two of
them could pick different jobs sharing that lock and both try to run them, which is
exactly what a lock exists to prevent. Which queues are being consumed differs per
worker, so it can't be part of the rule. Whether a job is due can only differ for an
instant, between workers fetching right as it becomes due: the database then refuses to
start the second job, and that worker finds no job this time.

### Pausing a lock until a given time

Because the mode is per job rather than per lock string, the two can be combined on
purpose. An `"ordered"` job acts as a **pause sentinel**: it reserves the lock even
though it cannot run yet, so every job behind it waits until it runs. Had the same job
been deferred as `"mutex"`, it would have stepped aside and the others would have kept
going.

This is useful for a rate-limited resource that tells you when the limit resets: insert
a no-op job with `lock_mode="ordered"`, a high priority, and `scheduled_at` set to the
reset time. The high priority is what puts the sentinel ahead of the jobs it should
hold back — a job only ever blocks the ones that come after it.

| id  | lock                 | priority | lock_mode | scheduled_at | effect                                    |
|-----|----------------------|---------:|-----------|--------------|-------------------------------------------|
| 101 | `resource:acme-api`  | 0        | `mutex`   |              | ready, held back by 104                   |
| 102 | `resource:acme-api`  | 0        | `mutex`   |              | ready, held back by 104                   |
| 103 | `resource:acme-api`  | 5        | `mutex`   | now + 24h    | blocks nothing while it waits             |
| 104 | `resource:acme-api`  | 9999     | `ordered` | now + 5m     | **pauses the whole lock for 5 minutes**   |
| 201 | `resource:other-api` | 0        | `mutex`   |              | different lock, unaffected                |

For 5 minutes nothing on `resource:acme-api` runs. Once 104 is done, 101 and 102 run one
at a time, while 103 keeps out of the way until it is due.

## Locks and Priority

When several jobs sharing a lock are runnable, they are processed one at a time, picked
by:

- descending priority (higher priority first), **then**
- ascending id (older job first)

Priority is checked first, so this is not plain FIFO: a newer, higher-priority job is
picked before an older, lower-priority one. Creation order only decides between jobs of
equal priority.

If a job with the same lock is running, all others with that lock wait, whatever their
priority. A high-priority job never interrupts a job already running.

This ordering applies to both lock modes. The only difference is which jobs take part:
with `"ordered"` every waiting job does, with `"mutex"` only those that are runnable.
