Get more context for task execution
-----------------------------------

When declaring a task, you can request for more context to be passed to the task
function::

    @app.task(..., pass_context=True)
    def mytask(context: procrastinate.JobContext, ...):
        ...

This serves multiple purposes. The first one is for introspection, logs, etc. The
`JobContext` object contains all sort of useful information about the worker that
executes the job.

The other useful feature is that you can pass arbitrary context elements using
`App.run_worker` (or `App.run_worker_async`) and its ``additional_context`` argument. In
this case the context the task function receives will have an ``additional_context``
attribute corresponding to the elements that were passed::

    @app.task(pass_context=True)
    def mytask(context: procrastinate.JobContext):
        http_session = context.additional_context["http_session"]
        return await http_session.get("www.example.com")

    async with AsyncSession() as http_session:
        await app.run_worker_async(additional_context={"http_session": http_session})
        ...

It may not be a good practice to use this ``additional_context`` object to share data
from tasks to tasks. In order to keep the least surprising behavior, Procrastinate will
try to keep modifications of this dictionary in one task from being visible by other
tasks: tasks receive a shallow copy of this dict instead of the dict itself.

That being said, the values kept in this dict are not processed by Procrastinate. Any
task mutating a value inside this dict will impact what all the concurrent and following
tasks will read.

Note that if you start a worker, providing it an ``additional_context`` dict, and then
modify the dict, the dict the tasks will receive will also be a shallow copy of the dict
at the time the worker started running.
