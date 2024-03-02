# Make the most out of the logging system

Procrastinate logs quite a few things, using structured logging. By default, the
messages can seem not very informative, but the details are not mixed into the log
messages, they are added as [extra] elements to the logs themselves.

This way, you can adapt the logs to whatever format suits your needs the most, using
a log filter:

```
import logging

class ProcrastinateLogFilter(logging.Filter):
    def filter(record):
        # adapt your record here
        return True

logging.getLogger("procrastinate").addFilter(ProcrastinateLogFilter)
```

One extra attribute that should be common to all procrastinate logs is
`action` attribute, that describes the event that triggered the logging. You can
match on this.

By default, extra attributes are not shown in the log output. The easiest way
to see them is to use a structured logging library such as [`structlog`].

If you want a minimal example of a logging setup that displays the extra
attributes without using third party logging libraries, look at the
[Django demo]

[extra]: https://timber.io/blog/the-pythonic-guide-to-logging/#adding-context
[`structlog`]: https://www.structlog.org/en/stable/
[Django demo]: https://github.com/procrastinate-org/procrastinate/blob/main/procrastinate_demos/demo_django/project/settings.py#L151
