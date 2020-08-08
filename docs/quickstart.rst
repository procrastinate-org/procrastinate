Quickstart
==========

In this section, we're going to build together a small application showcasing
Procrastinate and its everyday use.

Prerequisites & installation
----------------------------

If you already have a PostgreSQL database around, make sure to note the connection
parameters. Otherwise, we'll create one together with Docker_:

.. _Docker: https://docs.docker.com/

.. code-block:: console

    $ docker run --name pg-procrastinate --detach --rm -p 5432:5432 -e POSTGRES_PASSWORD=password postgres

.. note::

    If you need to stop the docker at some point, use ``docker stop pg-procrastinate``.

Within a virtualenv_, install Procrastinate with:

.. _virtualenv: https://packaging.python.org/tutorials/installing-packages/#creating-virtual-environments

.. code-block:: console

    (venv) $ pip install procrastinate


Create a Procrastinate application object
-----------------------------------------

We'll do this in a single file. Start an empty file named ``tutorial.py``::

    from procrastinate import AiopgConnector, App

    app = App(
        connector=AiopgConnector(host="localhost", user="postgres", password="password")
    )
    app.open()


The application will be the entry point for both:

- Declaring tasks (a.k.a job templates) to be launched by Procrastinate,
- Launching the worker that will consume the jobs created from those tasks.
- Applying Database schema

The ``App.open`` method is called to create the connection pool to the underlying
database. It will be automatically terminated upon garbage collection.

Prepare the database
--------------------

Install the PostgreSQL structure procrastinate needs in your database with:

.. code-block:: console

    (venv) $ export PYTHONPATH=.  # required for procrastinate to find "tutorial.app"
    (venv) $ procrastinate --app=tutorial.app schema --apply

.. note::

    The ``export PYTHONPATH=.`` above is required here for the ``procrastinate``
    command to be able to find your ``tutorial`` module, and the ``app`` object
    inside it. You wouldn't need to export ``PYTHONPATH`` if the ``tutorial``
    module was installed in the (virtual) Python environment.

Declare a task
--------------

In your file, add the following::

    # at the top of the file
    import random
    import time

    ...

    # at the bottom of the file
    @app.task(name="sum")
    def sum(a, b):
        time.sleep(random.random() * 5)  # Sleep up to 5 seconds
        return a + b

We've defined a task named "sum" that will wait a bit and compute the sum of two things.
(We could have added type annotations if we wanted).

At this point, nothing is running yet. We've just created a task, which is the template
(or blueprint) for a job.

Our task doesn't really have an impact on the world (a side effect). It doesn't write a
file, or update a database, it doesn't make an API call. In real life, this is a
problem, because at this point, all the job is doing is wasting CPU cycle. In our case,
though, we'll just monitor the standard output to see if our task executed successfully.
The return value of a task serves no other purpose than logging.

Launch a job
------------

We'll use the ``defer`` method of our task::

    import sys

    ...

    if __name__ == "__main__":
        a = int(sys.argv[1])
        b = int(sys.argv[2])
        print(f"Scheduling computation of {a} + {b}")
        sum.defer(a=a, b=b)  # This is the line that launches a job

You can launch your script now with:

.. code-block:: console

    (venv) $ python tutorial.py 2 3

But at this point, it should not do a lot. Feel free to create a few tasks in advance.

Let's run all of this, and check if we can spot the result in the logs.

Run a worker
------------

.. code-block:: console

    (venv) $ procrastinate --verbose --app=tutorial.app worker
    Launching a worker on all queues
    INFO:procrastinate.worker.worker:Starting worker on all queues
    INFO:procrastinate.worker.worker:Starting job sum[1](a=2, b=3)
    INFO:procrastinate.worker.worker:Job sum[1](a=2, b=3) ended with status: Success, lasted 1.822 s - Result: 5

Stop the worker with ``ctrl+c``.

In the logs, you can see that the result is 5, and the task took 1.8 seconds (in that
case).

Congratulations, you've successfully "procrastinated" the execution of your first job :)

Checking your jobs
------------------

.. code-block:: console

    (venv) $ procrastinate --app=tutorial.app healthchecks
    DB connection: OK
    todo: 0
    doing: 0
    succeeded: 1
    failed: 0


You can check that your application can access your database, and that your
procrastination was a success. For more precise monitoring, we can launch an interactive
shell:

.. code-block:: console

    (venv) $ procrastinate --app=tutorial.app shell
    Welcome to the procrastinate shell.   Type help or ? to list commands.

    procrastinate> help

    Documented commands (type help <topic>):
    ========================================
    EOF  cancel  exit  help  list_jobs  list_queues  list_tasks  retry

    procrastinate> list_jobs
    #1 sum on default - [succeeded]
    procrastinate> exit


Your final file
---------------

::

    import random
    import time
    import sys

    from procrastinate import App, AiopgConnector

    app = App(connector=AiopgConnector(host="localhost", user="postgres", password="password"))
    app.open()

    @app.task
    def sum(a, b):
        time.sleep(random.random() * 5)  # Sleep up to 5 seconds
        return a + b

    if __name__ == "__main__":
        a = int(sys.argv[1])
        b = int(sys.argv[2])
        print(f"Scheduling computation of {a} + {b}")
        sum.defer(a=a, b=b)  # This is the line that launches a job


Going further
-------------

To continue with practical steps, head to the "`howto_index`" section. For
example, have a look at the locks feature: `howto/locks`.

If you want to better understand some design decisions, head to the `Discussions
<discussions>` sections.


.. toctree::
   :maxdepth: 2

   howto_index
   discussions
