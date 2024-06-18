# Provide a job priority

We can assign an optional priority to a job. Jobs with higher priority will be
preferred by a worker. Priority is represented as an (positive or negative)
integer, where a larger number indicates a higher priority. If no priority is
specified, it defaults to 0.

Priority is used as a way to order available jobs. If a procrastinate worker
requests a job, and there is a high-priority job scheduled that is blocked by a
lock, and a low-priority job that is available, the worker will take
the low-priority job. Procrastinate will never wait for a high-priority job to
become available if there are lower-priority jobs already available.

## From the code

Launch a task with a priority of 5:

```python
my_task.configure(priority=5).defer()
```

## From the command line

```console
$ procrastinate defer --priority=5 path.to.my_task
```

:::{warning}
If your setup involves a continuous influx of jobs where workers are
perpetually busy (i.e., jobs are always queuing and workers are never idle),
using priorities could lead to excessive delays in job execution. For example,
if you have a job assigned a priority of -1 while all other jobs have a
priority of 0, the lower priority job might experience significant delays. In
a continuously busy system, this job could potentially take months to execute.
:::
