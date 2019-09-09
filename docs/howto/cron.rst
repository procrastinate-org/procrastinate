.. _cron:

Launch a task periodically
--------------------------

Launching anything periodically (every X units of time) is a really complicated
problem, mainly because of how the system is supposed to react when it's off or too
busy. Should it accumulate or discard jobs when it's too late and it couldn't
launch the jobs in time? How to define properly a unit of time, given there's
timezones, and leap years and such?

Procrastinate doesn't aim at answering these questions, but mature stable software
already has, in the form of `unix cron`_ and `systemd timers`_, to name just two.

.. _`unix cron`: https://en.wikipedia.org/wiki/Cron
.. _`systemd timers`: https://www.freedesktop.org/software/systemd/man/systemd.timer.html

That being said, Procrastinate tries to ease the use of these solutions by providing
a means to easily schedule jobs from the command line.

Whether you then decide to schedule multiple crons/timers, or a single one that will
in turn schedule the appropriate jobs is up to you, following your own constraints.

Launching a job from cron every 15 minutes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block::

    */15 * * * * /path/to/env/bin/procrastinate \
                    --app=dotted.path.to.app defer my.maintenance.task
