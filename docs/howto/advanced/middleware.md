# Add a middleware to the worker

Procrastinate allows you to add a middleware to the worker. This middleware
wraps the execution of every task, and can be used to add custom behavior before
or after the task is executed.

```python
def custom_middleware(process_task, context, worker):
    # do something before the task is executed
    result = await process_task()
    # do something after the task is executed
    return result

app.run_worker(middleware=custom_middleware)
```

The middleware is a coroutine that takes three arguments:
- `process_task`: a coroutine that runs the task
- `context`: a `JobContext` object that contains information about the job
- `worker`: the worker that runs the job

The middleware should await `process_task` to run the task and return the result.

The `worker` instance can be used to stop the worker from the middleware by
calling `worker.stop()`. This will stop the worker after the jobs currently being
processed are done.

# Add a middleware to a specific task

If you only want to wrap a specific task with a middleware you can use
your own decorator instead of `@app.task` and have this decorator
implement the actions you need and delegate the rest to `@app.task`.
It might look like this:

```python
import functools

def task(original_func=None, **kwargs):
    def wrap(func):
        def new_func(*job_args, **job_kwargs):
            # This is the custom part
            log_something()
            result = func(*job_args, **job_kwargs)
            log_something_else()
            return result

        wrapped_func = functools.update_wrapper(new_func, func, updated=())
        return app.task(**kwargs)(wrapped_func)

    if not original_func:
        return wrap

    return wrap(original_func)
```
