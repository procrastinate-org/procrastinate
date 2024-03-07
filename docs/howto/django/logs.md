# Get Procrastinate logs

Procrastinate logs to the `procrastinate` logger. You can configure it in your
`LOGGING` settings. By default, Procrastinate logs will be handled the same way
as the rest of your logs.

:::{note}
A lot of the interesting info in procrastinate logs is in the `extra` field of
the log record. By default, it won't be displayed in the console. If you use
a structured logging library such as [`structlog`], you should see all the
logs structured attributes.
:::

See {doc}`../production/logging` for more information.

Here is an example of a basic settings where you can configure Procrastinate
logs specifically. Without additional configuration, this will be lacking extra
fields.

```python
LOGGING = {
    "version": 1,
    "formatters": {
        "procrastinate": {
            "format": "%(asctime)s %(levelname)-7s %(name)s %(message)s"
        },
    },
    "handlers": {
        "procrastinate": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "procrastinate",
        },
    },
    "loggers": {
        "procrastinate": {
            "handlers": ["procrastinate"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}
```

Here is an example of settings where you get the structured logs without using an
extrernal library:

```python

# This emulates what a normal structured logging setup would get you out of the box
class ProcrastinateFilter(logging.Filter):
    # from https://github.com/madzak/python-json-logger/blob/master/src/pythonjsonlogger/jsonlogger.py#L19
    _reserved_log_keys = frozenset(
        """args asctime created exc_info exc_text filename
        funcName levelname levelno lineno module msecs message msg name pathname
        process processName relativeCreated stack_info thread threadName""".split()
    )
    def filter(self, record: logging.LogRecord):
        record.procrastinate = {}
        for key, value in vars(record).items():
            if not key.startswith("_") and key not in self._reserved_log_keys | {
                "procrastinate"
            }:
                record.procrastinate[key] = value  # type: ignore
        return True


LOGGING = {
    "version": 1,
    "formatters": {
        "procrastinate": {
            "format": "%(asctime)s %(levelname)-7s %(name)s %(message)s %(procrastinate)s"
        },
    },
    "handlers": {
        "procrastinate": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "procrastinate",
            "filters": ["procrastinate"],
        },
    },
    "filters": {
        "procrastinate": {
            "()": "dotted.path.to.ProcrastinateFilter",
            "name": "procrastinate",
        },
    },
    "loggers": {
        "procrastinate": {
            "handlers": ["procrastinate"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}
```


[`structlog`]: https://www.structlog.org/en/stable/
