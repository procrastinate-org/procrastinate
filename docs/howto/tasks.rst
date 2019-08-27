Define a task
-------------

You can specify a task with::

    @app.task(...)
    def mytask(argument, other_argument):
        ...

See :py:func:`App.task` for the exact parameters.

If you're ok with all the default parameters, it's ok to omit parentheses after
``task``::

    @app.task
    def mytask(argument, other_argument):
        ...
