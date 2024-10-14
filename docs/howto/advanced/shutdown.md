# Shutdown a worker

A worker will keep running until:
- it has the option `wait=False` (default is `True`) and there is no job left
- it has the option `install_signal_handlers=True` (default is `True`) and receives a `SIGINT/SIGTERM` signal
- [task.cancel](https://docs.python.org/3/library/asyncio-task.html#asyncio.Task.cancel) is called on the task created from `app.run_worker_async`

When a worker is requested to stop, it will attempt to gracefully shut down by waiting for all running jobs to complete.
If a `shutdown_graceful_timeout` option is specified, the worker will attempt to abort all jobs that have not completed by that time. Cancelling the `run_worker_async` task a second time also results in the worker aborting running jobs.

The worker will then wait for all jobs to complete.


:::{note}
The worker aborts its remaining jobs by:
- setting the context so that `JobContext.should_abort` returns `AbortReason.SHUTDOWN`
- calling [task.cancel](https://docs.python.org/3/library/asyncio-task.html#asyncio.Task.cancel) on the underlying asyncio task that runs the job when the job is asynchronous

Jobs that do not respect the request to abort will prevent the worker from shutting down until they complete. In a way, it will remain a graceful shutdown for those jobs even after `shutdown_graceful_timeout`.

For more information, see {doc}`./cancellation`.

Currently, Procrastinate does not provide a built-in method to forcefully terminate a worker. This is something you would want to do with your process manager (e.g. systemd, Docker, Kubernetes), which typically offers options to control process termination. In that case, your jobs will be considered stale, see {doc}`../production/retry_stalled_jobs`.
:::

## Examples

### Run a worker until no job is left

```python
async with app.open_async():
        await app.run_worker_async(wait=False)
        # at this point, the worker has gracefully shut down
```

### Run a worker until receiving a stop signal

```python
async with app.open_async():
    # give jobs up to 10 seconds to complete when a stop signal is received
    # all jobs still running after 10 seconds are aborted
    # In the absence of shutdown_graceful_timeout, the task will complete when all jobs have completed.
    await app.run_worker_async(shutdown_graceful_timeout=10)
```

### Run a worker until its Task is cancelled

```python
async with app.open_async():
    worker = asyncio.create_task(app.run_worker_async())
    # eventually
    worker.cancel()
    try:
        await worker
    except asyncio.CancelledError:
        # wait until all remaining jobs have completed, however long they take
        await worker
```

### Run a worker until its Task is cancelled with a shutdown timeout

```python
async with app.open_async():
    worker = asyncio.create_task(app.run_worker_async(shutdown_graceful_timeout=10))
    # eventually
    worker.cancel()
    try:
        await worker
    except asyncio.CancelledError:
        # at this point, the worker is shutdown.
        # Any job that took longer than 10 seconds to complete have aborted
        pass
```

### Cancel a worker Task and explicitly abort jobs after timeout

```python
async with app.open_async():
    # Notice that shutdown_graceful_timeout is not specified
    worker = asyncio.create_task(app.run_worker_async())

    # eventually
    worker.cancel()

    try:
            # give the jobs 10 seconds to complete and abort remaining jobs
        await asyncio.wait_for(worker, timeout=10)
    except asyncio.CancelledError:
        # all jobs have completed within 10 seconds
        pass
    except asyncio.TimeoutError:
        # one or more jobs took longer than 10 seconds and have aborted.
        pass

```
