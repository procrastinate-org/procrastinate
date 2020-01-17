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

    $ docker run --detach --rm -p 5432:5432 postgres

.. note::

    If you need to stop the docker at some point, use ``docker ps`` to find the
    container id and ``docker stop {container_id}``.

You'll also need ``psycopg2``, which is notoriously complex to install. Procrastinate
will install the ``psycopg2`` python package, but will expect the system to already
have the prerequisites (on ``Ubuntu``)::

    $ sudo apt install libpq-dev python-dev

.. note::

    On a different OS, if you experiment difficulties, we'll be grateful if you can tell
    us via an issue so that we improve this documentation.

Within a virtualenv_, install Procrastinate with:

.. _virtualenv: https://packaging.python.org/tutorials/installing-packages/#creating-virtual-environments

.. code-block:: console

    (venv) $ pip install procrastinate


Create a Procrastinate application object
-----------------------------------------

We'll do this in a single file. Start an empty file named ``tutorial.py``::

    from procrastinate import App, PostgresJobStore

    app = App(job_store=PostgresJobStore(host="localhost", user="postgres"))

The application will be the entry point for both:

- Declaring tasks (a.k.a job templates) to be launched by Procrastinate,
- Launching the worker that will consume the jobs created from those tasks.
- DB migrations

Prepare the database
--------------------

Install the PostgreSQL structure procrastinate needs in your database with:

.. code-block:: console

    (venv) $ export PYTHONPATH=.  # required for procrastinate to find "tutorial.app"
    (venv) $ procrastinate --app=tutorial.app migrate

.. note::

    The ``export PYTHONPATH=.`` above is required here for the ``procrastinate``
    command to be able to find your ``tutorial`` module, and the ``app`` object
    inside it. You wouldn't need to export ``PYTHONPATH`` if the ``tutorial``
    module was installed in the (virtual) Python environment.

Declare a task
--------------

In your file, add the following::

    import random  # at the top of the file

    ...

    @app.task(name="sum")
    def sum(a, b):
        sleep(random.random() * 5)  # Sleep up to 5 seconds
        print(a + b)

We've defined a task named "sum" that will wait a bit and compute the sum of two things.
(We could have added type annotations if we wanted).

At this point, nothing is running yet. We've just created a task, which is the template
(or blueprint) for a job.

Our task doesn't really have an impact on the world (a side effect). It doesn't write a
file, or update a database, it doesn't make an API call. In real life, this is a
problem, because at this point, all the job is doing is wasting CPU cycle. In our case,
though, we'll just monitor the standard output to see if our task executed successfully.

Launch a job
------------

We'll use the ``defer`` method of our task::

    import sys

    ...

    if __name__ == "__main__":
        a = int(sys.argv[2])
        b = int(sys.argv[3])
        print(f"Scheduling computation of {a} + {b}")
        sum.defer(a=a, b=b)  # This is the line that launches a job

You can launch your script now with:

.. code-block:: console

    (venv) $ python tutorial.py launch 2 3

But at this point, it should not do a lot. Feel free to create a few tasks in advance.

Let's run all of this, and check if we can spot the "print" call.

Run a worker
------------

.. code-block:: console

    (venv) $ export PYTHONPATH=.  # if not already done!
    (venv) $ procrastinate --verbose --app=tutorial.app worker

In the logs, you can see the values as they are computed.

Congratulations, you've successfully procrastinated the execution of your first task :)

Your final file
---------------

::

    import random
    import sys

    from procrastinate import App, PostgresJobStore

    app = App(job_store=PostgresJobStore(host="localhost", user="postgres"))

    @app.task
    def sum(a, b):
        sleep(random.random() * 5)  # Sleep up to 5 seconds
        print(a + b)

    if __name__ == "__main__":
        a = int(sys.argv[2])
        b = int(sys.argv[3])
        print(f"Scheduling computation of {a} + {b}")
        sum.defer(a=a, b=b)  # This is the line that launches a job


Going further
-------------

To continue with practical steps, head to the :ref:`How-to... <how-to>` section. For
example, have a look at the locks feature: :ref:`how-to-locks`.

If you want to better understand some design decisions, head to the :ref:`Discussions
<discussions>` sections.


.. toctree::
   :maxdepth: 2

   howto_index
   discussions
