How-to...
=========

Ensure jobs don't run concurrently and run in order
---------------------------------------------------

Let's imagine we have a task like this::

    @app.task
    def write_alphabet(letter):
        time.sleep(random.random() * 5)
        with open("/tmp/alphabet.txt", "a") as f:
            f.write(letter)

We write the letter we recieve to a file after wating for a
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
but cabbage will not select a job for completion as long as there is
a job currently processing with the same lock. Note that cabbage will
use postgres to search the jobs table for suitable jobs, meaning that
even if the database contains a high proportion of locked tasks, it will barely
affect cabbages's capacity to quickly find the free tasks. Also, identical
jobs will always be started in creation order, so we can be assured our
tasks will run sequentially and in order.

A good string identifier for the lock is a string identifier of
the shared resource, UUIDs are well suited for this.
If multiple resources are implicated, a combination
of their identifiers could be used (there's no hard
limit on the length of a lock string, but stay reasonable)

A task can only take a single lock so there's no dead-lock scenario possible
where 2 running tasks are waiting one another.

There is no mechanism in place to expire locks yet, but if a task fails
without the whole Python process crashing, it will free its lock.

Launch a job in the future
---------------------------

If a job is configured with a date in the future, it will run at the
first opportunity after that date. Let's launch the task that will
trigger the infamous 2018 bug::

    dt = datetime.datetime(2038, 1, 19, 3, 14, 7).replace(
        tzinfo=datetime.timezone.utc
    )
    create_bug.configure(schedule_at=dt).defer(crash_everything=True)

Also, you can configure a delay from now::

    clean.configure(schedule_in={"hours": 1, "minutes": 30}).defer()

The details on the parameters you can use are in the pendulum
`documentation <https://pendulum.eustace.io/docs/#addition-and-subtraction>`_
(because we use pendulum under the hood).

Add a task middleware
---------------------

As of today, Cabbage has no specific way of ensuring a piece of code runs
before or after every job. That being said, you can always decide to use
your own decorator instead of ``@app.task`` and have this decorator
implement the actions you need and delegate the rest to ``@app.task``.
It might look like this::

    def task(*args, **kwargs):
        def wrap(func):
            def new_func(*job_args, **job_kwargs):
                log_something()
                return func(*job_args, **job_kwargs)
                log_something_else()

            return app.task(*args, **kwargs)(new_func)
        return wrap

Then, define all of your tasks using this ``@task`` decorator.

Test your code that uses cabbage
--------------------------------

Cabbage defines an `InMemoryJobStore` that will speed-up your tests,
remove dependency to Postgres and allow you to have tasks run in a
controlled way.

To use it, you can do::

    app = cabbage.App(job_store={"name": "in_memory"})

    # Run the jobs your tests created, then stop
    # the worker:
    app.run_worker(only_once=True)

    # See the jobs created:
    print(app.job_store.jobs)

    # Reset the store between tests:
    app.job_store.reset()


Deploy Cabbage in a real environment
------------------------------------

We haven't done that yet, no advice to give.

Monitor cabbage in a real environment
-------------------------------------

We're in the process of writing an admin website and Rest API.
We'll update this section.
