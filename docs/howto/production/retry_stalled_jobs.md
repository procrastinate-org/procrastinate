# Retry stalled jobs

When a worker gets a `SIGINT` or `SIGTERM` signal requesting it to terminate it
waits for running jobs to finish before actually exiting. But, if the worker gets
a second `SIGINT` or `SIGTERM` signal, or if it's killed with `SIGKILL`, it will
terminate immediately, possibly leaving jobs with the `doing` status in the queue.
And, if no specific action is taken, these *stalled* jobs will remain in the queue
forever, and their execution will never resume.

To address this problem, Procrastinate workers update heartbeats at a regular
interval (every 10 seconds by default). If a worker is terminated without a regular
shutdown, the heartbeat of that worker will not be updated, and the worker will be
considered stalled. Jobs in the `doing` state of such stalled workers are considered
stalled as well and can be fetched by the with the {py:meth}`JobManager.get_stalled_jobs`
method.

:::{note}
Regular worker shutdowns delete the worker's heartbeat from the database. Heartbeats
of stalled worker are also pruned after a certain duration (30 seconds by default) to
avoid having too many heartbeats of old worker runs in the database, but stalled jobs
can still be detected.
:::

Those stalled jobs can then be retried for example by a periodic task. To enable
this add this task to your code:

```python
@app.periodic(cron="*/10 * * * *")
@app.task(queueing_lock="retry_stalled_jobs", pass_context=True)
async def retry_stalled_jobs(context, timestamp):
    stalled_jobs = await app.job_manager.get_stalled_jobs()
    for job in stalled_jobs:
        await app.job_manager.retry_job(job)
```

This defines a periodic task, configured to be deferred at every 10th minute. The task
retrieves all the jobs that have been in the `doing` status of workers that have not
received a heartbeat since the last (by default) 30 seconds. This duration can be
configured with the `seconds_since_heartbeat` parameter of the `get_stalled_jobs` method.

:::{note}
If you change the `seconds_since_heartbeat` parameter, make sure to also check the
`update_heartbeat_interval` and `stalled_worker_timeout` parameters of the worker
and adjust them accordingly.
:::

With this, if you have multiple workers, and, for some reason, one of them gets killed
while running jobs, then one of the remaining workers will run the
`retry_stalled_jobs` task, marking the stalled jobs for retry.

If you have specific rules for task retry (e.g. only some tasks should be retried, based
on specific parameters, or the duration before a task is considered stalled should
depend on the task), you're free to make the periodic task function more complex and add
your logic to it. See {py:meth}`JobManager.get_stalled_jobs` for details.

:::{warning}
`get_stalled_jobs` also accepts a `nb_seconds` parameter, which if set fetches
stalled jobs that have been in the `doing` state for more than the specified seconds
without even considering the worker heartbeat. This parameter is deprecated and will be
removed in a next major release as it may lead to wrongly retrying jobs that are still
running.
:::
