Ensure jobs run sequentially and in order
=========================================

In this section, we'll see **how** to setup locks. If you want to know
more about the locking feature (mainly the **why**), head to the Discussions
section (see `discussion-locks`).

When defering a job, we can provide a lock string to the ``configure`` method::

    my_task.configure(lock=customer.id).defer(a=1)
    my_other_task.configure(lock=customer.id).defer(b=2)

Or if we're defering the same task with the same lock multiple times, we can call
configure just once::

    job_description = my_task.configure(lock=customer.id)
    my_task.defer(a=1)
    my_task.defer(a=2)

In both case, this will ensure that the second task cannot run before the first one
has ended (succesfully or not).

.. warning::

    If a task is deferred with a lock and it has a ``scheduled_at`` arguments, then
    following tasks will still not run until after the task has been processed, which
    may be arbitrary far in the future.

    Similarily, if the oldest task of a lock is in a queue that no worker consumes, the
    other tasks will be blocked.
