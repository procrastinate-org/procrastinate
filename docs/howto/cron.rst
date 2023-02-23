Launch a task periodically
==========================

Procrastinate offers a way to schedule periodic deferring of tasks, with
`App.periodic`. It uses the `Unix cron`_ syntax::

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

Timestamp argument
------------------

By default, periodic tasks receive a single integer argument, named
``timestamp``. it represents the `Unix timestamp`__ of the date/time it was
scheduled for (which might be arbitrarily far in the past).

.. __: https://en.wikipedia.org/wiki/Unix_time

Scheduling a job multiple times with multiple arguments
-------------------------------------------------------

It's possible to pass additional arguments to `App.periodic`, they will be used
to configure the periodic task. Arguments are identical to `Task.configure`.

This can let you add multiple periodic schedules for a single task. If you do
that, you will need to pass a ``periodic_id`` argument to `App.periodic`, which
will be used by Procrastinate to distiguish the different schedules of the same
task.

Of course, you can also use arguments on `App.task` which will be common to all
schedules.

::

    @app.task(lock="do_something_lock")
    def do_something(timestamp: int, value: int):
        ...

    app.periodic(
        cron="*/5 * * * *",
        queue="foo",
        task_kwargs={"value": 1},
        periodic_id="foo",
    )(do_something)

    app.periodic(
        cron="*/8 * * * *",
        queue="bar",
        task_kwargs={"value": 2},
        periodic_id="bar",
    )(do_something)

In the example below, the ``do_something`` task would be deferred every 5
minutes on the queue ``"foo"`` with ``value=1`` **and** every 8 minutes on the
queue ``"bar"`` with ``value=2``. And either way, it would be deferred with the
lock ``"do_something_lock"``.

.. note::

    The arguments ``schedule_in`` and ``schedule_at`` of `Task.configure` would be
    confusing in this context, so they're ignored.

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

Dynamic scheduling
------------------

By default, for scheduling to work, the workers must know about the schedule, so the
calls to periodic (as a function or as a decorator) best be done right at task
definition time.

There are cases where you'll want the application to define the schedule, instead of it
being fixed in the source code. Here's an approach that will work in these scenarios:

- When users request periodic task scheduling, store this somewhere (probably in a
  database, like you'd do for other parts of you application)
- Have a single normal periodic task that runs as frequently as the most frequent
  setting your users can schedule tasks to (e.g. 1/min if that's the most often they can
  do it). On each run, the periodic task you implement will read the configuration from
  your backend, determine if something needs to be run  for the received timestamp (use
  the received timestamp, not ``time.time()`` because tasks might be running late, but the
  timestamp you receive is always right, defer corresponding tasks and that's it.
- The existing system already ensures that periodic tasks will run only once even if you
  have multiple workers.
