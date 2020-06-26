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

.. warning::

    The workers will defer the task at the requested period, but the corresponding
    jobs may be executed later, depending on how busy the workers are.

The cron syntax is on 5 columns (minute, hour, day, month, day of week). Here, an
optional 6th column is supported for seconds with the same syntax, allowing you to make
a periodic task as frequent as "1 per second".

Periodic task arguments
-----------------------

Periodic tasks receive a single integer argument, named ``timestamp``. it represents the
`Unix timestamp`__ of the date/time it was scheduled for.

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
