Get statistics regarding job executions
---------------------------------------

.. note::

    This is quite early-stage, likely to get a better interface in the future

At any point, you can look at the ``procrastinate_jobs`` table for information regarding
the success rate and the average number of retries of your jobs, but this doesn't
help if you're interested in time-related information, or if you want to search
for jobs based on the date of some events they went through.

For this, there's another table, ``procrastinate_events``, which contains rows pointing
to jobs in the ``procrastinate_jobs`` table, dates & times and events. Here's the
definition of each event:

``deferred``
    The job has been enqueued, will be executed by the workers later.
``started``
    The job was started by a worker.
``deferred_for_retry``
    The job failed, but according to the retry strategy, it should
    be retried (see :doc:`retry`).
``failed``
    The job failed, and will not be retried.
``succeeded``
    The job succeeded.
``cancelled``
    The job was waiting to be executed, but was ultimately placed to ``failed`` or
    ``succeeded``, bypassing execution.
``scheduled``
    This is a special event. When the job is deferred, this is the date where it's
    expected to run.
