# Pause a queue

We can pause a queue so that workers stop fetching its jobs, then resume it
later. This is useful to temporarily hold a queue's work, for example during a
maintenance window or while an external dependency is unavailable, without
stopping the worker process.

Pausing only stops the *fetching* of new jobs: jobs already being processed run
to completion, and pending jobs stay in the `todo` state until the queue is
resumed. Workers keep fetching jobs from the other queues.

The pause is stored in the database, so it is shared by every worker consuming
the queue and it survives a worker restart.

## Pause a queue

```python
# by using the sync method
app.job_manager.pause_queue("some_queue")
# or by using the async method
await app.job_manager.pause_queue_async("some_queue")
```

## Resume a queue

```python
# by using the sync method
app.job_manager.resume_queue("some_queue")
# or by using the async method
await app.job_manager.resume_queue_async("some_queue")
```

Resuming a queue that is not paused does nothing.

## Pause keys: several independent holders

Every pause is held under a *pause key* (`"default"` when not specified). A
queue is paused as long as it holds at least one key, and each key must be
resumed for the queue to start working again. This lets independent processes
pause the same queue without stepping on each other: if a deploy script and a
maintenance task both pause a queue and the deploy finishes first, its resume
only releases its own key — the queue stays paused until the maintenance task
resumes too.

```python
# deploy script
await app.job_manager.pause_queue_async("some_queue", pause_key="deploy")
...
await app.job_manager.resume_queue_async("some_queue", pause_key="deploy")

# maintenance task, meanwhile
await app.job_manager.pause_queue_async("some_queue", pause_key="maintenance")
...
await app.job_manager.resume_queue_async("some_queue", pause_key="maintenance")
```

## Resume all keys at once

A pause whose holder crashed before resuming (or was never going to resume)
stays in place until it is resumed under the same key. As an escape hatch,
`all_keys=True` removes every pause key from a queue, regardless of who holds
them:

```python
app.job_manager.resume_queue("some_queue", all_keys=True)
```

## List paused queues

```python
# by using the sync method
app.job_manager.list_paused_queues()
# or by using the async method
await app.job_manager.list_paused_queues_async()
```

This returns one `dict` per held pause key, with `queue_name`, `pause_key` and
`paused_at` keys — a queue paused by several holders appears once per key:

```python
[
    {"queue_name": "some_queue", "pause_key": "deploy", "paused_at": ...},
    {"queue_name": "some_queue", "pause_key": "maintenance", "paused_at": ...},
]
```

Both methods accept optional `queue` and `pause_key` filters:

```python
await app.job_manager.list_paused_queues_async(queue="some_queue")
```
