Make the most out of the logging system
---------------------------------------

Procrastinate logs quite a few things, using structured logging. By default, the
messages can seem not very informative, but the details are not mixed into the log
messages, they are added as extra_ elements to the logs themselves.

.. _extra: https://timber.io/blog/the-pythonic-guide-to-logging/#adding-context

This way, you can adapt the logs to whatever format suits your needs the most, using
a log filter::

    import logging

    class ProcrastinateLogFilter(logging.Filter):
        def filter(record):
            # adapt your record here
            return True

    logging.getLogger("procrastinate").addFilter(ProcrastinateLogFilter)

We'll try to document what attribute is available on each log, but one common thing is
the "action" attribute, that describes the event that triggered the logging. You can
match on this.
