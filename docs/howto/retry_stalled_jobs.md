# Retry stalled jobs

When a worker gets a `SIGINT` or `SIGTERM` signal requesting it to terminate it
waits for running jobs to finish before actually exiting. But, if the worker gets
a second `SIGINT` or `SIGTERM` signal, or if it's killed with `SIGKILL`, it will
terminate immediately, possibly leaving jobs with the `doing` status in the queue.
And, if no specific action is taken, these *stalled* jobs will remain in the queue
forever, and their execution will never resume.

To address that problem, Procrastinate offers functions that can be used in a periodic
task for retrying stalled jobs. Add the following in your code to enable automatic retry
of tasks after some time:

```python
# time in seconds for running jobs to be deemed as stalled
RUNNING_JOBS_MAX_TIME = 30

@app.periodic(cron="*/10 * * * *")
@app.task(queueing_lock="retry_stalled_jobs", pass_context=True)
async def retry_stalled_jobs(context, timestamp):
    stalled_jobs = await app.job_manager.get_stalled_jobs(
        nb_seconds=RUNNING_JOBS_MAX_TIME
    )
    for job in stalled_jobs:
        await app.job_manager.retry_job(job)
```

This defines a periodic task, configured to be deferred at every 10th minute. The task
retrieves all the jobs that have been in the `doing` status for more than
30 seconds, and restarts them (marking them with the `todo` status in the database).

With this, if you have multiple workers, and, for some reason, one of them gets killed
while running jobs, then one of the remaining workers will run the
`retry_stalled_jobs` task, marking the stalled jobs for retry.

If you have specific rules for task retry (e.g. only some tasks should be retried, based
on specific parameters, or the duration before a task is considered stalled should
depend on the task), you're free to make the periodic task function more complex and add
your logic to it. See {any}`JobManager.get_stalled_jobs` for details.

Also, note that if a task is considered stalled, it will be retried, but if it's
actually running, then you may have your task running twice. Make sure to only retry
a task when you're reasonably sure that it is not running anymore, so make sure your
stalled duration is sufficient.
