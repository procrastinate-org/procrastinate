Quickstart
==========

In this section, we're going to build together a small application showcasing
Procrastinate and its everyday use.

Prerequisites & installation
----------------------------

If you already have a PostgreSQL database around, make sure to note the connection
parameters. Otherwise, we'll create one together with Docker_, but is works all the
same if you'd rather install PostgreSQL directly in your system.

.. _Docker: https://docs.docker.com/

.. code-block:: console

    $ docker run --detach --rm -p 5432:5432 postgres

.. note::

    If you need to stop the docker at some point, use ``docker ps`` to find the
    container id and ``docker stop {container_id}``.

You'll also need ``psycopg2``, which is notoriously complex to install. Procrastinate
will install the ``psycopg2`` python package, but will expect the system to already
have the prerequesites (on ubuntu)::

    $ sudo apt install libpq-dev python-dev

.. note::
    On a different OS, if you experiment difficulties, we'll be grateful if you can tell
    us via an issue so that we improve this documentation.

Within a virtualenv_, install Procrastinate with:

.. _virtualenv: https://packaging.python.org/tutorials/installing-packages/#creating-virtual-environments

.. code-block:: console

    (venv) $ pip install procrastinate

Install the PostgreSQL structure procrastinate needs in your database with:

.. code-block:: console

    (venv) $ procrastinate migrate

.. note::

    Ok, you caught me, I wrote this doc in advance and the migrate command doesn't
    exist yet. Follow `#28`_ for details.

.. _`#28`: https://github.com/peopledoc/procrastinate/issues/28

Create a Procrastinate application object
-----------------------------------------

We'll do this in a single file. Start an empty file named ``tutorial.py``::

    from procrastinate import App, PostgresJobStore

    app = App(job_store=PostgresJobStore(host="localhost", user="postgres"))

The application will be the entry point for both:

- Declaring tasks (a.k.a job templates) to be launched by Procrastinate,
- Launching the worker that will consume the jobs created frome those tasks.

Declare a task
--------------

In your file, add the following::

    import random  # at the top of the file

    ...

    @app.task
    def sum(a, b):
        sleep(random.random() * 5)  # Sleep up to 5 seconds
        print(a + b)

We've defined a task that will wait a bit and compute the sum of two things. (We could
have added type annotations if we wanted).

At this point, nothing is running yet. We've just created a task, which is the template
(or blueprint) for a job.

Our task doesn't really have an impact on the world (a side effect). It doesn't write a
file, or update a database, it doesn't make an API call. In the real life, this is a
problem, because at this point, all the job is doing is wasting CPU cycle. In our case,
though, we'll just monitor the standard output to see if our task executed successfully,
we should be able to see the result of the "print" call

Time to...

Launch a job
------------

We'll use the ``defer`` method of our task::

    import sys

    ...

    if __name__ == "__main__":
        if sys.argv[1] == "job":
            a = int(sys.argv[2])
            b = int(sys.argv[3])
            print(f"Scheduling computation of {a} + {b}")
            sum.defer(a=a, b=b)  # This is the line that launches a job

You can launch your script now with:

.. code-block:: console

    (venv) $ python tutorial.py launch 2 3

But at this point, it should not do a lot. Feel free to create a few tasks in advance.

Run a worker
------------

 Edit the file this way::

    import logging
    ...

    if __name__ == "__main__":
        command = sys.argv[1]
        if command == "job":
            a = int(sys.argv[2])
            b = int(sys.argv[3])
            print(f"Scheduling computation of {a} + {b}")
            sum.defer(a=a, b=b)

        elif command == "worker":
            logging.basicConfig()
            app.run_worker()

.. note::

    In the future, you might be able to launch a worker from the command line without
    having to code anything. Follow `#28`_ for details.

.. _`#28`: https://github.com/peopledoc/procrastinate/issues/28

Now launch the worker with:

.. code-block:: console

    (venv) $ python tutorial.py worker

In the logs, you should see the values as they are computed.

Congratulations, you've succefully procrastinated the execution of your first task :)

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
        if sys.argv[1] == "job":
            a = int(sys.argv[2])
            b = int(sys.argv[3])
            print(f"Scheduling computation of {a} + {b}")
            sum.defer(a=a, b=b)  # This is the line that launches a job

        elif command == "worker":
            logging.basicConfig()
            app.run_worker()

Going further
-------------

To continue with practical steps, head to the :ref:`How-to... <how-to>` section. To take
the most out of Procrastinate, have a look at the :ref:`locks <locks>` feature.

If you want to better understand some design decisions, head to the :ref:`Discussions
<discussions>` sections.


.. toctree::
   :maxdepth: 2

   howto
   discussions
