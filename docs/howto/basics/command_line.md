# Use the command line

Procrastinate installs a command-line tool, which allows to do
some operations:

- Prepare your database for procrastinate (apply the database schema)

- Launch a worker

- Defer a task

- ...

The command-line tool can be launched using:

```console
$ procrastinate
```

or:

```console
$ python -m procrastinate
```

Please read the included help to get familiar with its commands and parameters:

:::{command-output} procrastinate --help
:::

## Define your app

When using the Procrastinate CLI, you'll almost always need to specify your app.
This can be done in two ways:

- Using the `--app` parameter:

  ```console
  $ procrastinate --app=dotted.path.to.app worker
  ```

- Using the `PROCRASTINATE_APP` environment variable:

  ```console
  $ export PROCRASTINATE_APP=dotted.path.to.app
  $ procrastinate worker
  ```

As a general rule, all parameters have an environment variable equivalent,
named `PROCRASTINATE_SOMETHING` or `PROCRASTINATE_SUBCOMMAND_SOMETHING`
where `SOMETHING` is the uppercased long name of the option, with `-`
replaced with `_` (e.g. `PROCRASTINATE_DEFER_UNKNOWN`). `procrastinate
--help` will show you the environment variable equivalent of each parameter.

In both case, the app you specify must have an asynchronous connector.

## Logging

Several options allow you to control how the command-line tool should log events:

- **Verbosity** controls the log level (you'll see messages of this level and above):

  | Flags          | Environment equivalent  | Log level |
  | -------------- | ----------------------- | --------- |
  |                | PROCRASTINATE_VERBOSE=0 | `info`    |
  | -v (or higher) | PROCRASTINATE_VERBOSE=1 | `debug`   |

  Note: Values beyond 1 have no additional effect.

- **Log level** allows explicit control over the logging level (mutually exclusive with `-v`):

  `--log-level=LEVEL` / `PROCRASTINATE_LOG_LEVEL=LEVEL` where `LEVEL` is one of:
  `debug`, `info`, `warning`, `error`, or `critical`.

  This option provides access to log levels not available through `-v` flags,
  such as `warning`, `error`, and `critical`. You cannot use `--log-level` and
  `-v` together.

  Examples:
  ```console
  $ procrastinate --log-level=warning worker
  $ PROCRASTINATE_LOG_LEVEL=error procrastinate worker
  ```

- **Log format**: `--log-format=` / `PROCRASTINATE_LOG_FORMAT=` lets you control how
  the log line will be formatted. It uses `%`-style placeholders by default.

- **Log format style**: `--log-format-style=` / `PROCRASTINATE_LOG_FORMAT_STYLE=`
  lets you choose different styles for the log-format, such as `{` or `$`.

For more information on log formats, refer to the [Python documentation](https://docs.python.org/3/library/logging.html?highlight=logging#logrecord-attributes)
