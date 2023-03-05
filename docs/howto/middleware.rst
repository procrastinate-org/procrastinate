Add a task middleware
---------------------

As of today, Procrastinate has no specific way of ensuring a piece of code runs
before or after every job. That being said, you can always decide to use
your own decorator instead of ``@app.task`` and have this decorator
implement the actions you need and delegate the rest to ``@app.task``.
It might look like this::

    import functools

    def task(original_func=None, *args, **kwargs):
        def wrap(func):
            def new_func(*job_args, **job_kwargs):
                # This is the custom part
                log_something()
                result = func(*job_args, **job_kwargs)
                log_something_else()
                return result

            wrapped_func = functools.update_wrapper(new_func, func, updated=())
            return app.task(*args, **kwargs)(wrapped_func)

    if not original_func:
        return wrap

    return wrap(original_func)

Then, define all of your tasks using this ``@task`` decorator.
