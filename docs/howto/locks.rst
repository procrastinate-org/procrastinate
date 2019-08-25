
.. _locks:

Ensure jobs don't run concurrently and run in order
---------------------------------------------------

Let's imagine we have a task like this::

    @app.task
    def write_alphabet(letter):
        time.sleep(random.random() * 5)
        with open("/tmp/alphabet.txt", "a") as f:
            f.write(letter)

We write the letter we receive to a file after waiting for a
random time (this is a simplified version of a real
world problem where tasks take a unforseeable amount of time
and share resources like a database).

We call it::

    write_alphabet.defer(letter="a")
    write_alphabet.defer(letter="b")
    write_alphabet.defer(letter="c")
    write_alphabet.defer(letter="d")

We could expect the following to be written in `alphabet.txt`::

    a
    b
    c
    d

And what we find is pretty much like this::

    d
    a
    c
    b

Jobs were taken from the queue in order, but if we have several
workers, they have been launched in parallel and given their duration
is random, the final result pretty much is too.

We can solve this problem by using locks::

    job_descritption = write_alphabet.configure(lock="/tmp/alphabet.txt")
    job_descritption.defer("a")
    job_descritption.defer("b")
    job_descritption.defer("c")
    job_descritption.defer("d")

In this case, our jobs might still be executed by any of the workers,
but Procrastinate will not select a job for completion as long as there is
a job currently processing with the same lock. Note that Procrastinate will
use PostgreSQL to search the jobs table for suitable jobs, meaning that
even if the database contains a high proportion of locked tasks, it will barely
affect Procrastinates's capacity to quickly find the free tasks. Also, identical
jobs will always be started in creation order, so we can be assured our
tasks will run sequentially and in order.

A good string identifier for the lock is a string identifier of
the shared resource, UUIDs are well suited for this.
If multiple resources are implicated, a combination
of their identifiers could be used (there's no hard
limit on the length of a lock string, but stay reasonable).

A task can only take a single lock so there's no dead-lock scenario possible
where 2 running tasks are waiting one another.

There is no mechanism in place to expire locks yet, but if a task fails
without the whole Python process crashing, it will free its lock.
