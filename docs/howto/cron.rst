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
- Workers are responsible for deferring periodic tasks. If there is no worker running,
  then periodic tasks will not get scheduled. On the other hand, even if you have
  multiple workers, periodic tasks will only be deferred once per period.
- When a worker starts, it will defer periodic tasks that have not been deferred yet
  but a task that is more than 10 minutes late will not be deferred. This value is
  configurable in the `App`.

Periodic task arguments
-----------------------

Periodic tasks receive a single integer argument, named ``timestamp``. it represents the
`Unix timestamp`__ of the date/time it was scheduled for (which might be arbitrarily far
in the past).

.. __: https://en.wikipedia.org/wiki/Unix_time

Queue, lock, queuing lock
-------------------------

Procrastinate itself takes care of deferring the periodic jobs, which means you don't
have to opportunity to specify a given queue, lock or queueing lock at defer time.
Fortunately, you can define all of those on the task itself, provided that you
plan to have the same value for every job::

    @app.periodic(cron="*/5 * * * *")
    @app.task(
        queue="healthchecks",
        lock="healthchecks",
        queueing_lock="healthchecks"
    )
    def run_healthchecks(timestamp: int):
        ...

The value of those parameters is static, but you could put different values on different
workers. If the same task is periodically deferred to different queues, each job will be
independent::

    @app.periodic(cron="*/5 * * * *")
    @app.task(
        queue=f"healthchecks_{my_worker_id}",
    )
    def run_healthchecks(timestamp: int):
        ...

In this setup, each worker (with differing values of ``my_worker_id``) would defer their
own healthcheck jobs, independently from other workers.

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
