# Retry a Failed Job Manually

Sometimes a manual retry, for instance, after we fix an integration's configuration, can be practical.
This is why the job_manager offers an API to do so. Retrying a `failed` job will set the status of the job
back to `todo` while keeping the history of events in place. The action of retrying a failed job,
is also recording a new Event of type `retried`.

:warning: if the job is not `failed`, the method will raise an error.

## Retry a failed job programatically

```python
app.job_manager.retry_failed_job_by_id(
    job.id, job.priority, job.queue_name, job.lock
)
# or by using the async method
await app.job_manager.retry_failed_job_by_id_async(
    job.id, job.priority, job.queue_name, job.lock
)
```

## For django users

An admin action `Retry Failed Job` can also be invoked from the table view of the
Procrastinate Jobs.
