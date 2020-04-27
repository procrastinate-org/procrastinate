Define a task
-------------

You can specify a task with::

    @app.task(...)
    def mytask(argument, other_argument):
        ...

See `App.task` for the exact parameters.

If you're OK with all the default parameters, you can omit parentheses after
``task``::

    @app.task
    def mytask(argument, other_argument):
        ...
