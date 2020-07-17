Launch a job in the future
--------------------------

This section is about launching a job once, but in the future. You may want to read
the `periodic launch <cron>` section.

From the code
^^^^^^^^^^^^^

If a job is configured with a date in the future, it will run at the
first opportunity after that date. Let's launch the task that will
trigger the infamous 2038 bug::

    dt = datetime.datetime(2038, 1, 19, 3, 14, 7).replace(
        tzinfo=datetime.timezone.utc
    )
    create_bug.configure(schedule_at=dt).defer(crash_everything=True)

Also, you can configure a delay from now::

    clean.configure(schedule_in={"hours": 1, "minutes": 30}).defer()

The details on the parameters you can use are in the `python documentation`_.

.. _`python documentation`: https://docs.python.org/3/library/datetime.html#timedelta-objects

From the command line
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: console

    $ procrastinate defer \
        --at=2038-01-19T03:14:07Z \
        path.to.create_bug '{"crash_everything": true}'

Or for an interval (in seconds):

.. code-block:: console

    $ procrastinate defer --in=5400 path.to.clean
