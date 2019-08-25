Launch a job in the future
--------------------------

If a job is configured with a date in the future, it will run at the
first opportunity after that date. Let's launch the task that will
trigger the infamous 2038 bug::

    dt = datetime.datetime(2038, 1, 19, 3, 14, 7).replace(
        tzinfo=datetime.timezone.utc
    )
    create_bug.configure(schedule_at=dt).defer(crash_everything=True)

Also, you can configure a delay from now::

    clean.configure(schedule_in={"hours": 1, "minutes": 30}).defer()

The details on the parameters you can use are in the `pendulum documentation`_
(because we use pendulum under the hood).

.. _`pendulum documentation`: https://pendulum.eustace.io/docs/#addition-and-subtraction
