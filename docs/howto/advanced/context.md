# Get more context for task execution

When declaring a task, you can request for more context to be passed to the task
function:

```
@app.task(..., pass_context=True)
def mytask(context: procrastinate.JobContext, ...):
    ...
```

This serves multiple purposes. The first one is for introspection, logs, etc. The
{py:class}`JobContext` object contains all sort of useful information about the worker that
executes the job.

The other useful feature is that you can pass arbitrary context elements using
{py:meth}`App.run_worker` (or {py:meth}`App.run_worker_async`) and its `additional_context` argument. In
this case the context the task function receives will have an `additional_context`
attribute corresponding to the elements that were passed:

```
@app.task(pass_context=True)
def mytask(context: procrastinate.JobContext):
    http_session = context.additional_context["http_session"]
    return await http_session.get("www.example.com")

async with AsyncSession() as http_session:
    await app.run_worker_async(additional_context={"http_session": http_session})
    ...
```

This feature is not supposed to be used for passing data from a task to a
future task. In order to deter this behavior, Procrastinate will
not keep modifications made to the `additional_context` dict after the worker has
started.

That being said, the values kept in this dict are not processed by Procrastinate. Any
task mutating a value inside this dict will impact what all the concurrent and following
tasks will read.
