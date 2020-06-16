Add a task middleware
---------------------

As of today, Procrastinate has no specific way of ensuring a piece of code runs
before or after every job. That being said, you can always decide to use
your own decorator instead of ``@app.task`` and have this decorator
implement the actions you need and delegate the rest to ``@app.task``.
It might look like this::

    def task(*args, **kwargs):
        def wrap(func):
            def new_func(*job_args, **job_kwargs):
                # This is the custom part
                log_something()
                result = func(*job_args, **job_kwargs)
                log_something_else()
                return result

            return app.task(*args, **kwargs)(new_func)
        return wrap

Then, define all of your tasks using this ``@task`` decorator.
