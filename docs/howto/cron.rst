Launch a task periodically
==========================

Procrastinate offers a way to schedule periodic deferring of tasks. It uses the
`Unix cron`_ syntax::

    # scheduled at the 0th minute of each hour
    @app.periodic(cron="0 * * * *")
    @app.task
    def cleanup_foobar(timestamp: int):
        ...

    # scheduled every 5 minutes
    @app.periodic(cron="*/5 * * * *")
    @app.task
    def run_healthchecks(timestamp: int):
        ...

.. _`Unix cron`: https://en.wikipedia.org/wiki/Cron

Internally, each worker is responsible for ensuring that each periodic task is deferred
in time, and the database is responsible for making sure deferring only happens once per
period, even with multiple workers. This means that you can have high availability
periodic scheduling: as long as at least one worker is up, the tasks will be deferred.

The cron syntax is on 5 columns (minute, hour, day, month, day of week). Here, an
optional 6th column is supported for seconds with the same syntax, allowing you to make
a periodic task as frequent as "1 per second".

Caveats
-------

When using periodic tasks there are a few things to know:

- Tasks are periodically **deferred** but their execution time depends on the state of
  your queue. If your workers are overwhelmed with long tasks, periodic executions could
  be delayed. One possible solution involves using queues to make sure short tasks are
  not delayed by long tasks.
- Workers are responsible for deferring periodic tasks. If not a single worker is
  running, then periodic tasks will not get scheduled. On the other hand, even if you
  have multiple workers, periodic tasks will only be deferred once per period.
- If a worker is occupied by a long-standing synchronous task, it will not be available
  to defer periodic tasks. If you use sync tasks, ensure that at least one of your
  workers is assigned tasks that are usually shorter to run than your shortest periodic
  task interval. This is especially true for tasks that run every second.
- When a worker wakes up, it will defer periodic tasks that have not been deferred yet
  but:

  - Only a single job for each task will be deferred (if a task is scheduled to run
    every minute, and it missed 5 minutes, when the first worker starts, it will only
    defer the last missed task, not the 4 previous ones).
  - A task that is more than 10 minutes late will not be launched. This value is
    configurable in the `App`.

Periodic task arguments
-----------------------

Periodic tasks receive a single integer argument, named ``timestamp``. it represents the
`Unix timestamp`__ of the date/time it was scheduled for (which might be arbitrarily far
in the past).

.. __: https://en.wikipedia.org/wiki/Unix_time

Using cron
----------

It's also perfectly valid to leverage cron or `systemd timers`_ to periodically
defer jobs, and queuing locks to keep them from accumulating in case of a slowdown in
processing.

Here's how to use cron to launch a job every 15 minutes, without launching a new
job when one (with the same queueing lock) is already waiting in the queue:

.. code-block:: console

    */15 * * * * /path/to/env/bin/procrastinate --app=dotted.path.to.app defer \
            --queueing-lock=maintenance --ignore-already-enqueued my.maintenance.task


.. _`systemd timers`: https://www.freedesktop.org/software/systemd/man/systemd.timer.html
