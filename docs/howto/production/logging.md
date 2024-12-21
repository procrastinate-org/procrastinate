# Make the most out of the logging system

Procrastinate logs quite a few things, using structured logging. By default, the
messages can seem not very informative, but the details are not mixed into the log
messages, they are added as [extra] elements to the logs themselves.

This way, you can adapt the logs to whatever format suits your needs the most, using
a log filter:

```python
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
[Django demo].

:::{note}
When using the `procrastinate` CLI, procrastinate sets up the logs for you,
but the only customization available is `--log-format` and `--log-format-style`.
If you want to customize the log format further, you will need run your own
script that calls procrastinate's app methods.
:::

## `structlog`

[`structlog`](https://www.structlog.org/en/stable/index.html) needs to be
configured in order to have `procrastinate`'s logs be formatted uniformly
with the rest of your application.

The `structlog` docs has a [how to](https://www.structlog.org/en/stable/standard-library.html#rendering-using-structlog-based-formatters-within-logging).

A minimal configuration would look like:

```python
shared_processors = [
    structlog.contextvars.merge_contextvars,
    structlog.stdlib.add_logger_name,
    structlog.stdlib.add_log_level,
    structlog.processors.StackInfoRenderer(),
    structlog.dev.set_exc_info,
    structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
]

structlog.configure(
    processors=shared_processors,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

formatter = structlog.stdlib.ProcessorFormatter(
    foreign_pre_chain=shared_processors,
    processors=[
        structlog.stdlib.ProcessorFormatter.remove_processors_meta,
        structlog.dev.ConsoleRenderer(event_key="message"),
    ],
)

handler = logging.StreamHandler()
handler.setFormatter(formatter)

root = logging.getLogger()
root.addHandler(handler)
root.setLevel(log_level)
```

[extra]: https://timber.io/blog/the-pythonic-guide-to-logging/#adding-context
[`structlog`]: https://www.structlog.org/en/stable/
[Django demo]: https://github.com/procrastinate-org/procrastinate/blob/main/procrastinate_demos/demo_django/project/settings.py#L151
